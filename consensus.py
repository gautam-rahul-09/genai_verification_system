import re


def to_number(value):
    """
    Converts extracted values into float safely.
    Handles:
    - "6300000"
    - "63,00,000"
    - "₹63,00,000"
    - "Rs. 63,00,000/-"
    - "63 lakh"
    - "6.3 crore"
    - "INR 74.50 Lakh"
    """

    if value is None:
        return None

    # Already numeric
    if isinstance(value, (int, float)):
        return float(value)

    # Convert string
    if isinstance(value, str):
        text = value.lower().strip()

        # Remove currency symbols and common words
        text = text.replace("₹", "")
        text = text.replace("rs.", "")
        text = text.replace("rs", "")
        text = text.replace("inr", "")
        text = text.replace("/-", "")
        text = text.replace(",", "")
        text = text.strip()

        # Handle crore/lakh explicitly
        crore_match = re.search(r"(\d+(\.\d+)?)\s*crore", text)
        if crore_match:
            return float(crore_match.group(1)) * 10000000

        lakh_match = re.search(r"(\d+(\.\d+)?)\s*lakh", text)
        if lakh_match:
            return float(lakh_match.group(1)) * 100000

        # Extract the first large number sequence
        num_match = re.search(r"\d+(\.\d+)?", text)
        if num_match:
            return float(num_match.group(0))

    return None


def agree(value_a, value_b, tolerance=0.05):
    value_a = to_number(value_a)
    value_b = to_number(value_b)

    if value_a is None or value_b is None:
        return False

    if value_a == 0 or value_b == 0:
        return False

    bigger = max(value_a, value_b)
    smaller = min(value_a, value_b)

    ratio = bigger / smaller

    # 🔥 Auto-scale correction if ratio is exactly 10 or 100
    if ratio in [10, 100]:
        return True

    diff = abs(value_a - value_b) / bigger
    return diff <= tolerance
