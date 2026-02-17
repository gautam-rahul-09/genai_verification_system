def detect_document_type(text: str) -> str:
    text_lower = text.lower()

    # SALE / PROPERTY DOCUMENT
    sale_keywords = [
        "sale deed",
        "deed of sale",
        "sale consideration",
        "agreement for sale",
        "conveyance",
        "property described",
        "schedule a",
        "immovable property"
    ]

    # LOAN DOCUMENT
    loan_keywords = [
        "loan sanction",
        "sanction letter",
        "home loan",
        "loan amount",
        "sanctioned amount",
        "credit facility"
    ]

    for kw in sale_keywords:
        if kw in text_lower:
            return "SALE_DEED"

    for kw in loan_keywords:
        if kw in text_lower:
            return "LOAN_DOC"

    return "UNKNOWN"
