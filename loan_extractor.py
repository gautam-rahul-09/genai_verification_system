import re
from llm_models.model_a import ModelA
from llm_models.model_b import ModelB
from consensus import to_number


# ---------------------------------------------------------
# Helper: Convert words like "Thirty Five Lakhs" → 3500000
# ---------------------------------------------------------
def words_to_number(words: str):
    if not words:
        return None

    words = words.lower()

    words = words.replace("rupees", "").replace("only", "").strip()

    num_words = {
        "zero": 0,
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19,
        "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
    }

    multipliers = {
        "hundred": 100,
        "thousand": 1000,
        "lakh": 100000,
        "lakhs": 100000,
        "crore": 10000000,
        "crores": 10000000
    }

    tokens = words.split()

    total = 0
    current = 0

    for token in tokens:
        if token in num_words:
            current += num_words[token]

        elif token in multipliers:
            mult = multipliers[token]

            if current == 0:
                current = 1

            current = current * mult
            total += current
            current = 0

    total += current

    return total if total > 0 else None



# ---------------------------------------------------------
# Helper: Validate numeric vs word amount
# ---------------------------------------------------------
def validate_numeric_vs_words(numeric_value, word_value):
    if numeric_value is None or word_value is None:
        return numeric_value

    numeric_value = float(numeric_value)
    word_value = float(word_value)

    # If close enough (within 5%)
    diff = abs(numeric_value - word_value) / max(numeric_value, word_value)

    if diff <= 0.05:
        return numeric_value

    # If numeric is 10x or 100x smaller → trust words
    ratio = max(numeric_value, word_value) / min(numeric_value, word_value)

    if ratio in [10, 100]:
        return word_value

    return None


# ---------------------------------------------------------
# Main Extractor Class
# ---------------------------------------------------------
class LoanDocumentExtractor:
    def __init__(self):
        self.model_a = ModelA()
        self.model_b = ModelB()

    def extract_financials(self, document_text: str, doc_type: str) -> dict:

        if doc_type == "SALE_DEED":
            field = "property_value"
            prompt = f"""
You are a strict BFSI financial extraction AI.

Extract ONLY property value from this SALE DEED.

Return STRICT JSON only:
{{
  "property_value_numeric": number_or_null,
  "property_value_words": string_or_null,
  "vendor_name": string_or_null,
  "vendee_name": string_or_null
}}

Rules:
- Use sale consideration / market value if clearly mentioned.
- Extract numeric amount exactly.
- Extract value in words if present (e.g. "Thirty Five Lakhs").
- Do NOT guess.
- If missing return null.

Text:
{document_text}
"""

        elif doc_type == "LOAN_DOC":
            field = "loan_amount"
            prompt = f"""
You are a strict BFSI loan extraction AI.

Extract ONLY sanctioned loan amount from this LOAN document.

Return STRICT JSON only:
{{
  "loan_amount_numeric": number_or_null,
  "loan_amount_words": string_or_null,
  "applicant_name": string_or_null
}}

Rules:
- Must be explicitly mentioned as sanctioned loan amount.
- Extract numeric amount exactly.
- Extract amount in words if present (e.g. "Thirty Five Lakhs").
- Do NOT guess.
- If missing return null.

Text:
{document_text}
"""
        else:
            return {"status": "UNKNOWN_DOC"}

        # ---------------------------------------------------------
        # Dual LLM extraction
        # ---------------------------------------------------------
        result_a = self.model_a.extract_json(prompt)
        result_b = self.model_b.extract_json(prompt)

        # If model unavailable
        if result_a.get("status") == "MODEL_UNAVAILABLE" or result_b.get("status") == "MODEL_UNAVAILABLE":
            return {"status": "HUMAN_REVIEW_REQUIRED", "reason": "One model unavailable"}

        # ---------------------------------------------------------
        # Extract values depending on doc_type
        # ---------------------------------------------------------
        if doc_type == "LOAN_DOC":
            val_a = to_number(result_a.get("loan_amount_numeric"))
            val_b = to_number(result_b.get("loan_amount_numeric"))

            words_a = result_a.get("loan_amount_words")
            words_b = result_b.get("loan_amount_words")

            applicant_a = result_a.get("applicant_name")
            applicant_b = result_b.get("applicant_name")

            # Convert word amount to number
            words_num_a = words_to_number(words_a)
            words_num_b = words_to_number(words_b)

            # Validate numeric vs words for each model
            final_a = validate_numeric_vs_words(val_a, words_num_a)
            final_b = validate_numeric_vs_words(val_b, words_num_b)

            # If still mismatch
            if final_a is None or final_b is None:
                return {
                    "status": "DISAGREEMENT",
                    "reason": "Loan amount mismatch between numeric and words",
                    "model_a_value": val_a,
                    "model_b_value": val_b,
                    "model_a_words": words_a,
                    "model_b_words": words_b,
                    "agreement": False
                }

            # If models still disagree heavily
            diff = abs(final_a - final_b) / max(final_a, final_b)
            if diff > 0.05:
                return {
                    "status": "DISAGREEMENT",
                    "reason": "Loan amount mismatch between models",
                    "model_a_value": final_a,
                    "model_b_value": final_b,
                    "model_a_unit": f"{final_a/100000:.2f} lakh",
                    "model_b_unit": f"{final_b/100000:.2f} lakh",
                    "agreement": False,
                    "applicant_name_a": applicant_a,
                    "applicant_name_b": applicant_b
                }

            final_value = int((final_a + final_b) / 2)

            return {
                "loan_amount": final_value,
                "model_a_value": final_a,
                "model_b_value": final_b,
                "agreement": True,
                "applicant_name": applicant_b or applicant_a,
                "model_a_unit": f"{final_a/100000:.2f} lakh",
                "model_b_unit": f"{final_b/100000:.2f} lakh",
                "final_unit": f"{final_value/100000:.2f} lakh"
            }

        # ---------------------------------------------------------
        # SALE DEED CASE
        # ---------------------------------------------------------
        if doc_type == "SALE_DEED":
            val_a = to_number(result_a.get("property_value_numeric"))
            val_b = to_number(result_b.get("property_value_numeric"))

            words_a = result_a.get("property_value_words")
            words_b = result_b.get("property_value_words")

            vendor_a = result_a.get("vendor_name")
            vendor_b = result_b.get("vendor_name")

            vendee_a = result_a.get("vendee_name")
            vendee_b = result_b.get("vendee_name")

            words_num_a = words_to_number(words_a)
            words_num_b = words_to_number(words_b)

            final_a = validate_numeric_vs_words(val_a, words_num_a)
            final_b = validate_numeric_vs_words(val_b, words_num_b)

            if final_a is None or final_b is None:
                return {
                    "status": "DISAGREEMENT",
                    "reason": "Property value mismatch between numeric and words",
                    "model_a_value": val_a,
                    "model_b_value": val_b,
                    "model_a_words": words_a,
                    "model_b_words": words_b,
                    "agreement": False
                }

            diff = abs(final_a - final_b) / max(final_a, final_b)
            if diff > 0.05:
                return {
                    "status": "DISAGREEMENT",
                    "reason": "Property value mismatch between models",
                    "model_a_value": final_a,
                    "model_b_value": final_b,
                    "model_a_unit": f"{final_a/100000:.2f} lakh",
                    "model_b_unit": f"{final_b/100000:.2f} lakh",
                    "agreement": False
                }

            final_value = int((final_a + final_b) / 2)

            return {
                "property_value": final_value,
                "model_a_value": final_a,
                "model_b_value": final_b,
                "agreement": True,
                "vendor_name": vendor_b or vendor_a,
                "vendee_name": vendee_b or vendee_a,
                "model_a_unit": f"{final_a/100000:.2f} lakh",
                "model_b_unit": f"{final_b/100000:.2f} lakh",
                "final_unit": f"{final_value/100000:.2f} lakh"
            }
