import pytesseract
from PIL import Image
import PyPDF2
import os
from pdf2image import convert_from_path


class OCREngine:
    """
    OCR Engine for extracting text from images and PDFs using Tesseract OCR.
    Supports both text-based PDFs and scanned/image PDFs.
    """

    def __init__(self, tesseract_cmd: str = None, poppler_path: str = None):
        """
        Initialize OCR Engine.

        Args:
            tesseract_cmd: Path to tesseract.exe (if not in PATH)
            poppler_path: Path to poppler bin folder (Windows only)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.poppler_path = poppler_path

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file."""
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        If PDF has embedded text layer -> extract via PyPDF2.
        If scanned PDF -> convert pages to images and run OCR.
        """
        try:
            # Try extracting embedded text
            text = self._extract_text_from_pdf(pdf_path)

            # If no embedded text, use OCR
            if not text.strip():
                text = self._ocr_pdf_pages(pdf_path)

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text directly from a PDF if it contains text layers."""
        text = []
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception:
            return ""

    def _ocr_pdf_pages(self, pdf_path: str) -> str:
        """
        Convert PDF pages to images using pdf2image and perform OCR.
        Requires poppler installed (Windows).
        """
        text = []

        images = convert_from_path(pdf_path, poppler_path=self.poppler_path)

        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            text.append(page_text)

        return "\n".join(text)

    def process_document(self, file_path: str) -> str:
        """Process a document (PDF or image) and return extracted text."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".pdf":
            return self.extract_text_from_pdf(file_path)

        elif file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return self.extract_text_from_image(file_path)

        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
