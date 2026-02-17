import json
from typing import Dict
from openai import AzureOpenAI


class ModelB:
    """
    ModelB = Cloud LLM (Azure OpenAI).
    Used ONLY for independent verification.
    """

    def __init__(self):
        self.available = True

        try:
            self.client = AzureOpenAI(
                api_key="9JEAg9qfuLiySXdILk1szsc76GQLg3lln5sxARmYbKIZOuoz5CzYJQQJ99CBACHYHv6XJ3w3AAAAACOGm61J",
                api_version="2024-02-01",
                azure_endpoint="https://ai-gautamrahul29058886ai866540254902.openai.azure.com/"
            )
        except Exception:
            print("⚠️ Azure OpenAI not available. ModelB disabled.")
            self.available = False

    # ---------------------------------------------------------
    # 🔹 STRUCTURED JSON EXTRACTION
    # ---------------------------------------------------------
    def extract_json(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1200
    ) -> Dict:

        if not self.available:
            return {
                "status": "MODEL_UNAVAILABLE",
                "error": "Azure OpenAI not available"
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict information extraction engine. "
                            "Return VALID JSON only. No explanations."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
