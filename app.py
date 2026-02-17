import streamlit as st
import tempfile
import os
import re

from ocr.ocr_engine import OCREngine
from loan_extractor import LoanDocumentExtractor
from rules_engine.policy_rules import MAX_LTV_ABOVE_75L
from document_classifier import detect_document_type

from llm_models.model_a import ModelA
from llm_models.model_b import ModelB


st.set_page_config(page_title="GenAI Verification Layer", layout="wide")

st.title("🏦 GenAI Verification Layer (Dual LLM Verification)")
st.write(
    "Upload **Sale Deed**, **Loan Sanction Letter**, and **Aadhaar PDF**. "
    "The system verifies RBI LTV compliance and identity matching using **two independent AI models**."
)

ocr = OCREngine()
extractor = LoanDocumentExtractor()

# Aadhaar extraction models
model_a = ModelA()
model_b = ModelB()


# -------------------------------------------------------
# Utility Functions
# -------------------------------------------------------
def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def normalize_name(name: str):
    if not name:
        return None
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^a-z\s]", "", name)
    return name


def names_match(name1: str, name2: str):
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    if not n1 or not n2:
        return False

    if n1 == n2:
        return True

    return n1 in n2 or n2 in n1


def mask_aadhaar(aadhaar: str):
    if not aadhaar:
        return None

    digits = re.sub(r"\D", "", str(aadhaar))

    if len(digits) == 12:
        return "XXXX-XXXX-" + digits[-4:]

    return aadhaar


def format_indian_units(amount):
    """
    Converts numeric amount into lakh/crore string.
    Example:
    3500000 => 35.0 lakh
    12000000 => 1.2 crore
    """
    if amount is None:
        return None

    amount = float(amount)

    if amount >= 10000000:
        return f"{round(amount / 10000000, 2)} crore"
    elif amount >= 100000:
        return f"{round(amount / 100000, 2)} lakh"
    else:
        return str(amount)


# -------------------------------------------------------
# UI Display Functions
# -------------------------------------------------------
def show_dual_llm_results(title, data, field_name):
    st.subheader(title)

    col1, col2, col3 = st.columns(3)

    model_a_val = data.get("model_a_value")
    model_b_val = data.get("model_b_value")

    model_a_unit = data.get("model_a_unit") or format_indian_units(model_a_val)
    model_b_unit = data.get("model_b_unit") or format_indian_units(model_b_val)

    with col1:
        st.markdown("### 🧠 Model-A (Ollama)")
        if model_a_val is not None:
            st.write(f"₹{int(float(model_a_val)):,}")
            st.caption(f"≈ {model_a_unit}")
        else:
            st.write("Not Found")

    with col2:
        st.markdown("### ☁️ Model-B (Azure OpenAI)")
        if model_b_val is not None:
            st.write(f"₹{int(float(model_b_val)):,}")
            st.caption(f"≈ {model_b_unit}")
        else:
            st.write("Not Found")

    with col3:
        st.markdown("### 🔍 Agreement")
        if data.get("agreement") is True:
            st.success("MATCH ✅")
        else:
            st.error("MISMATCH ❌")

    st.markdown("### ✅ Final Accepted Value")
    final_val = data.get(field_name)
    final_unit = data.get("final_unit") or format_indian_units(final_val)

    if final_val is not None:
        st.info(f"Using: ₹{int(float(final_val)):,}")
        st.caption(f"≈ {final_unit}")
    else:
        st.warning("No final value available.")


def extract_aadhaar_details(text: str):
    prompt = f"""
You are a strict Aadhaar extraction AI.

Extract Aadhaar identity details.

Return STRICT JSON only:
{{
  "name": string_or_null,
  "dob": string_or_null,
  "aadhaar_number": string_or_null
}}

Rules:
- Aadhaar number must be 12 digits if present.
- Do NOT guess.
- If not found return null.

Text:
{text}
"""

    a = model_a.extract_json(prompt)
    b = model_b.extract_json(prompt)

    return {"model_a": a, "model_b": b}


def show_aadhaar_verification(a_data):
    st.subheader("🤖 Aadhaar Dual LLM Extraction")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Model-A (Ollama)")
        st.json(a_data["model_a"])

    with col2:
        st.markdown("### ☁️ Model-B (Azure OpenAI)")
        st.json(a_data["model_b"])


# -------------------------------------------------------
# Upload UI
# -------------------------------------------------------
st.header("📤 Upload Documents")

col1, col2, col3 = st.columns(3)

with col1:
    sale_deed_file = st.file_uploader("📄 Upload Sale Deed PDF", type=["pdf"])

with col2:
    loan_letter_file = st.file_uploader("📄 Upload Loan Sanction Letter PDF", type=["pdf"])

with col3:
    aadhaar_file = st.file_uploader("🪪 Upload Aadhaar PDF", type=["pdf"])


# -------------------------------------------------------
# Verification Button
# -------------------------------------------------------
if st.button("🚀 Verify Documents"):

    if not sale_deed_file or not loan_letter_file or not aadhaar_file:
        st.error("⚠️ Please upload Sale Deed + Loan Sanction Letter + Aadhaar PDF.")
        st.stop()

    sale_deed_path = save_uploaded_file(sale_deed_file)
    loan_letter_path = save_uploaded_file(loan_letter_file)
    aadhaar_path = save_uploaded_file(aadhaar_file)

    st.info("🔍 Processing documents... Please wait.")

    # -------------------------------------------------------
    # SALE DEED
    # -------------------------------------------------------
    st.header("📄 Sale Deed Verification")

    sale_text = ocr.process_document(sale_deed_path)

    if not sale_text or len(sale_text.strip()) < 50:
        st.error("❌ Sale deed is unreadable or empty.")
        st.stop()

    sale_type = detect_document_type(sale_text)
    st.write("Detected Document Type:", sale_type)

    sale_data = extractor.extract_financials(sale_text, sale_type)

    if sale_data.get("status") in ["HUMAN_REVIEW_REQUIRED", "DISAGREEMENT"]:
        st.error("❌ AI mismatch or model unavailable in Sale Deed extraction.")
        st.warning("➡️ Human review required.")
        st.json(sale_data)
        st.stop()

    show_dual_llm_results("🤖 Dual LLM Extraction (Sale Deed)", sale_data, "property_value")

    property_value = sale_data.get("property_value")
    vendor_name = sale_data.get("vendor_name")
    vendee_name = sale_data.get("vendee_name")

    st.subheader("🧾 Sale Deed Identity Details")
    st.write("Vendor (Seller):", vendor_name)
    st.write("Vendee (Buyer):", vendee_name)

    if property_value is None:
        st.error("❌ Property value not found in Sale Deed.")
        st.stop()

    # -------------------------------------------------------
    # LOAN SANCTION LETTER
    # -------------------------------------------------------
    st.header("📄 Loan Sanction Letter Verification")

    loan_text = ocr.process_document(loan_letter_path)

    if not loan_text or len(loan_text.strip()) < 50:
        st.error("❌ Loan sanction letter is unreadable or empty.")
        st.stop()

    loan_type = detect_document_type(loan_text)
    st.write("Detected Document Type:", loan_type)

    loan_data = extractor.extract_financials(loan_text, loan_type)

    if loan_data.get("status") in ["HUMAN_REVIEW_REQUIRED", "DISAGREEMENT"]:
        st.error("❌ AI mismatch or model unavailable in Loan Document extraction.")
        st.warning("➡️ Human review required.")
        st.json(loan_data)
        st.stop()

    show_dual_llm_results("🤖 Dual LLM Extraction (Loan Document)", loan_data, "loan_amount")

    loan_amount = loan_data.get("loan_amount")
    applicant_name = loan_data.get("applicant_name")

    st.subheader("🧾 Loan Applicant Details")
    st.write("Applicant Name:", applicant_name)

    if loan_amount is None:
        st.error("❌ Loan amount not found in Loan Sanction Letter.")
        st.stop()

    # -------------------------------------------------------
    # AADHAAR EXTRACTION
    # -------------------------------------------------------
    st.header("🪪 Aadhaar Verification")

    aadhaar_text = ocr.process_document(aadhaar_path)

    if not aadhaar_text or len(aadhaar_text.strip()) < 50:
        st.error("❌ Aadhaar document is unreadable or empty.")
        st.stop()

    aadhaar_extraction = extract_aadhaar_details(aadhaar_text)

    show_aadhaar_verification(aadhaar_extraction)

    aadhaar_name = aadhaar_extraction["model_b"].get("name")
    aadhaar_dob = aadhaar_extraction["model_b"].get("dob")
    aadhaar_number = mask_aadhaar(aadhaar_extraction["model_b"].get("aadhaar_number"))

    st.subheader("📌 Aadhaar Extracted Details (Final)")
    st.write("Name:", aadhaar_name)
    st.write("DOB:", aadhaar_dob)
    st.write("Aadhaar Number:", aadhaar_number)

    if aadhaar_name is None:
        st.error("❌ Aadhaar name not extracted. Human review required.")
        st.stop()

    # -------------------------------------------------------
    # IDENTITY MATCHING
    # -------------------------------------------------------
    st.header("🧾 Identity Match Verification")

    if applicant_name is None:
        st.error("❌ Applicant name not found in Loan Document.")
        st.warning("➡️ Human review required.")
        st.stop()

    applicant_match = names_match(aadhaar_name, applicant_name)
    vendor_match = names_match(aadhaar_name, vendor_name)
    vendee_match = names_match(aadhaar_name, vendee_name)

    st.write("Aadhaar Name:", aadhaar_name)
    st.write("Loan Applicant Name:", applicant_name)
    st.write("Sale Deed Vendor:", vendor_name)
    st.write("Sale Deed Vendee:", vendee_name)

    st.write("Aadhaar matches Loan Applicant:", "✅ Yes" if applicant_match else "❌ No")
    st.write("Aadhaar matches Vendor:", "✅ Yes" if vendor_match else "❌ No")
    st.write("Aadhaar matches Vendee:", "✅ Yes" if vendee_match else "❌ No")

    if not applicant_match:
        st.error("❌ Aadhaar does not match Loan Applicant.")
        st.warning("➡️ Human review required.")
        st.stop()

    if not (vendor_match or vendee_match):
        st.error("❌ Aadhaar does not match any Sale Deed party (Vendor/Vendee).")
        st.warning("➡️ Human review required.")
        st.stop()

    st.success("✅ Identity Verified: Aadhaar matches Loan Applicant and Sale Deed party.")

    # -------------------------------------------------------
    # RBI LTV DECISION
    # -------------------------------------------------------
    st.header("✅ RBI Compliance Check (LTV Rule)")

    ltv = loan_amount / property_value

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Loan Amount", f"₹{loan_amount:,}", format_indian_units(loan_amount))

    with col2:
        st.metric("Property Value", f"₹{property_value:,}", format_indian_units(property_value))

    with col3:
        st.metric("Computed LTV", round(ltv, 2))

    st.write("RBI Max Allowed LTV:", MAX_LTV_ABOVE_75L)

    if ltv > MAX_LTV_ABOVE_75L:
        st.error("❌ RBI VIOLATION: LTV exceeds allowed limit")
    else:
        st.success("✅ RBI COMPLIANT: LTV is within allowed limit")

    # -------------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------------
    st.header("📌 Final Verification Summary")

    st.success("✔ Sale Deed processed through BOTH AI models (Ollama + Azure).")
    st.success("✔ Loan Sanction Letter processed through BOTH AI models (Ollama + Azure).")
    st.success("✔ Aadhaar processed through BOTH AI models (Ollama + Azure).")
    st.success("✔ Identity verification completed (Vendor/Vendee + Applicant).")
    st.success("✔ RBI LTV policy applied successfully.")
    st.success("✔ Human review not required.")
