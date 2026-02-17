from llm_models.model_a import ModelA
from llm_models.model_b import ModelB
from consensus import agree


class AadhaarExtractor:
    def __init__(self):
        self.model_a = ModelA()
        self.model_b = ModelB()

    def extract_aadhaar_details(self, text: str):
        prompt = f"""
Extract Aadhaar card identity details.

Return strict JSON:
{{
  "name": string_or_null,
  "dob": string_or_null,
  "aadhaar_number": string_or_null
}}

Rules:
- Aadhaar number should be 12 digits if present.
- If missing return null.
- Do not guess.

Text:
{text}
"""

        a = self.model_a.extract_json(prompt)
        b = self.model_b.extract_json(prompt)

        return {
            "model_a": a,
            "model_b": b
        }
