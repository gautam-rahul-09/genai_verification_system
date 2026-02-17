import json
import ollama
from typing import Dict, List
from . import prompts


class ModelA:
    """
    ModelA = Local LLM (Ollama).
    Used for extraction, NOT final decision-making.
    """

    def __init__(self, model: str = "llama3:8b"):
        self.model = model
        self.available = True

        try:
            ollama.list()
        except Exception:
            print("⚠️ Ollama not running. ModelA disabled.")
            self.available = False

    # ---------------------------------------------------------
    # 🔹 STRUCTURED JSON EXTRACTION
    # ---------------------------------------------------------
    def extract_json(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 1200
    ) -> Dict:

        if not self.available:
            return {
                "status": "MODEL_UNAVAILABLE",
                "error": "Ollama service not running"
            }

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a strict information extraction engine. "
                        "Return VALID JSON only. No explanation."
                    )
                },
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "format": "json"
                }
            )

            return json.loads(response["message"]["content"])

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
