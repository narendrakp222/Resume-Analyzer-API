import fitz  # PyMuPDF
import re
from fastapi import HTTPException, status
from app.core.logger import logger


class PDFService:
    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """
        Extract text content from PDF file on disk using PyMuPDF.
        """
        try:
            doc = fitz.open(file_path)
            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                extracted_pages.append(page.get_text("text"))
            doc.close()
            
            full_text = "\n".join(extracted_pages)
            return PDFService.clean_text(full_text)
        except Exception as e:
            logger.error(f"Failed to extract PDF text from {file_path}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse PDF file: {str(e)}"
            )

    @staticmethod
    def extract_text_from_bytes(content_bytes: bytes) -> str:
        """
        Extract text content directly from PDF byte buffer.
        """
        try:
            doc = fitz.open(stream=content_bytes, filetype="pdf")
            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                extracted_pages.append(page.get_text("text"))
            doc.close()

            full_text = "\n".join(extracted_pages)
            return PDFService.clean_text(full_text)
        except Exception as e:
            logger.error(f"Failed to extract PDF text from bytes: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid or corrupted PDF file: {str(e)}"
            )

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        """
        if not text:
            return ""
        # Replace multiple whitespace characters with single spaces
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
