import json
import re
from typing import Dict, Any, Optional
from llm_models.model_a import ModelA

class RBIComplianceAnalyst:
    """
    RBI Compliance Analyst AI for extracting regulatory rules from housing finance circulars.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        """
        Initialize the RBI compliance analyst.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.llm = ModelA(model=model_name)
    
    def extract_rbi_rules(self, document_text: str) -> Dict[str, Any]:
        """
        Extract RBI regulatory rules from housing finance circular text.
        
        Args:
            document_text: The text content of the RBI circular
            
        Returns:
            Dictionary containing extracted rules in strict JSON format
        """
        prompt = f"""
You are an RBI compliance analyst AI. Read the following RBI Housing Finance circular and extract regulatory rules in strict JSON format.

Extract these fields:
1. max_ltv_general – Maximum Loan to Value ratio allowed.
2. max_ltv_above_75L – LTV limit when loan amount is above ₹75 lakh.
3. risk_weight_rules – Any risk weight rules related to LTV.
4. provisioning_rules – Any provisioning or capital requirement mentioned.
5. important_conditions – Any special conditions or exceptions.

Return output strictly in valid JSON.
Do NOT add explanation or commentary.
Do NOT include markdown.
Only return JSON.

Document Text:
{document_text}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You are an RBI compliance analyst that extracts regulatory rules in strict JSON format."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.llm.chat(
                model=self.llm.model,
                messages=messages,
                options={
                    'temperature': 0.1,
                    'num_predict': 1000,
                    'format': 'json'
                }
            )
            
            # Parse the JSON response
            result = response['message']['content']
            return json.loads(result)
            
        except Exception as e:
            # Fallback to rule-based extraction if LLM fails
            return self._fallback_extraction(document_text)
    
    def _fallback_extraction(self, document_text: str) -> Dict[str, Any]:
        """
        Fallback rule-based extraction for common RBI housing finance rules.
        """
        rules = {
            "max_ltv_general": None,
            "max_ltv_above_75L": None,
            "risk_weight_rules": [],
            "provisioning_rules": [],
            "important_conditions": []
        }
        
        # Extract LTV ratios using regex
        ltv_patterns = [
            r'(\d+)%.*loan to value',
            r'LTV.*?(\d+)%',
            r'loan to value.*?(\d+)%'
        ]
        
        for pattern in ltv_patterns:
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            if matches:
                rules["max_ltv_general"] = f"{matches[0]}%"
                break
        
        # Extract specific LTV for above 75 lakh
        above_75_patterns = [
            r'above.*?75.*?lakhs?.*?(\d+)%',
            r'₹75.*?lakhs?.*?(\d+)%',
            r'exceeding.*?75.*?lakhs?.*?(\d+)%'
        ]
        
        for pattern in above_75_patterns:
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            if matches:
                rules["max_ltv_above_75L"] = f"{matches[0]}%"
                break
        
        # Extract risk weight rules
        risk_weight_patterns = [
            r'risk weight.*?(\d+)%?',
            r'(\d+)%?.*?risk weight'
        ]
        
        for pattern in risk_weight_patterns:
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            for match in matches:
                rules["risk_weight_rules"].append(f"{match}%")
        
        # Extract provisioning rules
        provisioning_keywords = ['provisioning', 'provision', 'capital adequacy', 'capital requirement']
        for keyword in provisioning_keywords:
            if keyword.lower() in document_text.lower():
                # Extract sentences containing provisioning keywords
                sentences = re.split(r'[.!?]+', document_text)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        rules["provisioning_rules"].append(sentence.strip())
        
        # Extract important conditions
        condition_keywords = ['condition', 'exception', 'subject to', 'provided that', 'however']
        for keyword in condition_keywords:
            if keyword.lower() in document_text.lower():
                sentences = re.split(r'[.!?]+', document_text)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        rules["important_conditions"].append(sentence.strip())
        
        return rules
    
    def save_extracted_rules(self, rules: Dict[str, Any], output_path: str) -> None:
        """
        Save extracted rules to JSON file.
        
        Args:
            rules: Extracted rules dictionary
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
            
if __name__ == "__main__":
    from ocr.ocr_engine import OCREngine

    pdf_path = "data/policies/73MCF02072012.pdf"
    output_path = "data/policies/extracted_rules.json"

    print("Extracting RBI text...")
    ocr = OCREngine()
    text = ocr.process_document(pdf_path)

    analyst = RBIComplianceAnalyst()
    print("Extracting structured RBI rules using LLM...")
    rules = analyst.extract_rbi_rules(text)

    print("Saving rules to JSON...")
    analyst.save_extracted_rules(rules, output_path)

    print("Done. Rules saved to:", output_path)
