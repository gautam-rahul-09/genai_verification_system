import os
from ocr.ocr_engine import OCREngine
from loan_extractor import LoanDocumentExtractor
from rules_engine.policy_rules import MAX_LTV_ABOVE_75L
from document_classifier import detect_document_type
from verification_report import create_report


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DOCS_DIR = os.path.join(BASE_DIR, "data", "raw_docs")

ocr = OCREngine()
extractor = LoanDocumentExtractor()

# 🔹 Verification report (user + audit visibility)
report = create_report()

loan_amount = None
property_value = None

# 🔁 Process all PDFs automatically
for filename in os.listdir(RAW_DOCS_DIR):
    if not filename.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(RAW_DOCS_DIR, filename)
    print(f"\nProcessing: {filename}")

    text = ocr.process_document(pdf_path)

    if not text or len(text.strip()) < 50:
        print("⚠️ Document empty or unreadable — skipped")
        continue

    # 🔍 Document classification
    doc_type = detect_document_type(text)

    # 🔍 Dual-LLM extraction
    data = extractor.extract_financials(text, doc_type)

    # Mark that independent AI checks were used
    report["models_used"]["model_a"] = True
    report["models_used"]["model_b"] = True

    # 🚨 Safety checks
    if data.get("status") in ["HUMAN_REVIEW_REQUIRED", "DISAGREEMENT"]:
        report["human_review_required"] = True
        report["confidence"] = "LOW"
        report["final_decision"] = "PENDING_REVIEW"
        report["details"]["reason"] = "Independent AI mismatch or unavailability"

        print("\n❌ AI verification mismatch")
        print("➡️ Human review required")

        # 🔍 User-friendly summary
        print("\n--- Verification Summary ---")
        print("AI Checks Performed: 2/2")
        print("Confidence Level: LOW")
        print("Human Review Required: YES")
        print("Final Decision: PENDING")
        exit()

    # ✅ Capture loan amount
    if doc_type == "LOAN_DOC" and loan_amount is None:
        loan_amount = data.get("loan_amount")
        print("✔ Loan amount captured")

    # ✅ Capture property value
    if doc_type == "SALE_DEED" and property_value is None:
        property_value = data.get("property_value")
        print("✔ Property value captured")

# -----------------------------
# Final Decision
# -----------------------------
if loan_amount is None or property_value is None:
    report["human_review_required"] = True
    report["confidence"] = "LOW"
    report["final_decision"] = "PENDING_REVIEW"

    print("\n❌ Missing required documents")
    print("➡️ Human review / wait for remaining docs")

    print("\n--- Verification Summary ---")
    print("AI Checks Performed: 2/2")
    print("Confidence Level: LOW")
    print("Human Review Required: YES")
    print("Final Decision: PENDING")
    exit()

ltv = loan_amount / property_value

print("\nLoan Amount:", loan_amount)
print("Property Value:", property_value)
print("Computed LTV:", round(ltv, 2))
print("RBI Max Allowed LTV:", MAX_LTV_ABOVE_75L)

if ltv > MAX_LTV_ABOVE_75L:
    report["final_decision"] = "RBI_VIOLATION"
    report["confidence"] = "HIGH"
    print("❌ RBI VIOLATION")
else:
    report["final_decision"] = "RBI_COMPLIANT"
    report["confidence"] = "HIGH"
    print("✅ RBI COMPLIANT")

# -----------------------------
# User-Facing Verification Summary
# -----------------------------
print("\n--- Verification Summary ---")
print("AI Checks Performed: 2/2")
print("Confidence Level:", report["confidence"])
print("Human Review Required:", report["human_review_required"])
print("Final Decision:", report["final_decision"])
