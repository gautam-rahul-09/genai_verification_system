import json
import re

RULES_PATH = "data/policies/extracted_rules.json"

with open(RULES_PATH, "r", encoding="utf-8") as f:
    rules = json.load(f)

def extract_percentage(text):
    if not text:
        return None
    match = re.search(r'(\d+)\s*%', str(text))
    if match:
        return float(match.group(1)) / 100
    return None

MAX_LTV_GENERAL = extract_percentage(rules.get("max_ltv_general"))
MAX_LTV_ABOVE_75L = extract_percentage(rules.get("max_ltv_above_75L"))

# fallback (industry practice)
if MAX_LTV_GENERAL is None:
    MAX_LTV_GENERAL = 0.80

if MAX_LTV_ABOVE_75L is None:
    MAX_LTV_ABOVE_75L = 0.75


RISK_WEIGHT_RULES = rules.get("risk_weight_rules")
PROVISIONING_RULES = rules.get("provisioning_rules")
IMPORTANT_CONDITIONS = rules.get("important_conditions")
