from datetime import datetime

def create_report():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "models_used": {
            "model_a": False,
            "model_b": False
        },
        "agreement": {},
        "confidence": "UNKNOWN",
        "final_decision": None,
        "human_review_required": False,
        "details": {}
    }
