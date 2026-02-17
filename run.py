import os
import argparse
import json
from typing import List, Dict, Optional
from pathlib import Path

from ocr.ocr_engine import OCREngine
from llm_models.model_a import ModelA

class GenAIVerificationSystem:
    """
    Main class for the GENAI Verification System.
    Handles document processing, OCR, and verification using LLMs.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the verification system.
        
        Args:
            config: Configuration dictionary with optional keys:
                   - tesseract_cmd: Path to Tesseract executable (if not in PATH)
                   - model_name: Name of the Ollama model to use (default: "llama3:8b")
        """
        self.config = config or {}
        
        # Initialize OCR engine
        self.ocr_engine = OCREngine(
            tesseract_cmd=self.config.get('tesseract_cmd')
        )
        
        # Initialize LLM model
        self.llm = ModelA(
            model=self.config.get('model_name', 'llama3:8b')
        )
    
    def process_document(
        self, 
        file_path: str, 
        verification_criteria: List[str]
    ) -> Dict:
        """
        Process a document and verify it against the given criteria.
        
        Args:
            file_path: Path to the document (PDF or image)
            verification_criteria: List of criteria to verify against
            
        Returns:
            Dictionary containing verification results
        """
        # Validate file exists
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "status": "error"}
        
        try:
            # Extract text using OCR
            print(f"Extracting text from: {file_path}")
            extracted_text = self.ocr_engine.process_document(file_path)
            
            if not extracted_text.strip():
                return {
                    "error": "No text could be extracted from the document.",
                    "status": "error"
                }
            
            # Generate a summary
            print("Generating document summary...")
            summary = self.llm.summarize_text(extracted_text)
            
            # Verify against criteria
            print("Verifying document against criteria...")
            verification_results = self.llm.verify_text(
                text=extracted_text,
                verification_criteria=verification_criteria
            )
            
            return {
                "status": "success",
                "file_path": file_path,
                "extracted_text": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                "summary": summary,
                "verification_results": verification_results,
                "metadata": {
                    "file_size": os.path.getsize(file_path),
                    "file_extension": os.path.splitext(file_path)[1].lower(),
                    "processing_time": "TBD"  # You can add timing logic here
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "file_path": file_path
            }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="GENAI Document Verification System")
    parser.add_argument(
        "file_path", 
        type=str, 
        help="Path to the document to verify (PDF or image)"
    )
    parser.add_argument(
        "--criteria", 
        type=str,
        nargs='+',
        default=[
            "The document contains a clear title",
            "The document has a logical structure",
            "The document includes references or citations if needed"
        ],
        help="List of verification criteria"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="llama3:8b",
        help="Name of the Ollama model to use (default: llama3:8b)"
    )
    parser.add_argument(
        "--tesseract-cmd", 
        type=str, 
        default=None,
        help="Path to Tesseract executable (if not in PATH)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the verification system
    verifier = GenAIVerificationSystem({
        'model_name': args.model,
        'tesseract_cmd': args.tesseract_cmd
    })
    
    # Process the document
    print(f"\nProcessing document: {args.file_path}")
    print("-" * 50)
    
    result = verifier.process_document(
        file_path=args.file_path,
        verification_criteria=args.criteria
    )
    
    # Print results
    if result.get('status') == 'success':
        print("\nVerification Results:")
        print("=" * 50)
        print(f"Document: {result['file_path']}")
        print(f"\nSummary:\n{result['summary']}")
        
        print("\nVerification Criteria:")
        print("-" * 50)
        for item in result['verification_results'].get('verification_results', []):
            print(f"\nCriterion: {item.get('criterion')}")
            print(f"Met: {item.get('met')} (Confidence: {item.get('confidence', 'N/A')})")
            print(f"Explanation: {item.get('explanation')}")
        
        print("\n" + "=" * 50)
        print(f"Overall Verdict: {result['verification_results'].get('overall_verdict', 'N/A')}")
    else:
        print("\nError processing document:")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
