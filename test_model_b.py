from llm_models.model_b import ModelB

model = ModelB()

prompt = """
Extract property value.

Return JSON:
{ "property_value": number_or_null }

Text:
Sale consideration is Rs. 63,00,000.
"""

print(model.extract_json(prompt))
