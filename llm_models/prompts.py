from typing import Dict, List, Optional

class VerificationPrompts:
    """
    Contains prompt templates for the verification system.
    """
    
    @staticmethod
    def get_verification_prompt(text: str, verification_criteria: List[str]) -> str:
        """
        Generate a verification prompt for the LLM.
        
        Args:
            text: The text to verify
            verification_criteria: List of criteria to verify against
            
        Returns:
            Formatted prompt string
        """
        criteria_str = '\n'.join(f"- {criterion}" for criterion in verification_criteria)
        
        return f"""
        Please analyze the following text and verify it against these criteria:
        {criteria_str}
        
        Text to verify:
        ---
        {text}
        ---
        
        For each criterion, provide:
        1. Whether the text meets the criterion (Yes/No/Partially)
        2. A brief explanation
        3. Confidence level (High/Medium/Low)
        
        Format your response as a JSON object with the following structure:
        {{
            "verification_results": [
                {{
                    "criterion": "[criterion text]",
                    "met": "[Yes/No/Partially]",
                    "explanation": "[explanation]",
                    "confidence": "[High/Medium/Low]"
                }}
            ],
            "overall_verdict": "[Overall verification status]",
            "summary": "[Brief summary of findings]"
        }}
        """

    @staticmethod
    def get_summary_prompt(text: str, max_length: int = 300) -> str:
        """
        Generate a summary of the given text.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of the summary in characters
            
        Returns:
            Prompt for generating a summary
        """
        return f"""
        Please provide a concise summary of the following text in {max_length} characters or less.
        Focus on the key points and main ideas.
        
        Text to summarize:
        ---
        {text}
        ---
        
        Summary:
        """

    @staticmethod
    def get_qa_prompt(question: str, context: str) -> str:
        """
        Generate a prompt for question answering.
        
        Args:
            question: The question to answer
            context: The context to find the answer in
            
        Returns:
            Formatted QA prompt
        """
        return f"""
        Based on the following context, answer the question. If the answer cannot be found in the context, 
        respond with "I don't have enough information to answer this question."
        
        Context:
        ---
        {context}
        ---
        
        Question: {question}
        Answer:
        """
