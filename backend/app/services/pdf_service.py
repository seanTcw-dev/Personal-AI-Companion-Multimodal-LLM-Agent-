import os
import logging
from pypdf import PdfReader
from typing import Optional

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        # Determine the sandbox directory (same logic as TelegramBot)
        # Assuming app structure: backend/app/services/pdf_service.py
        base_dir = os.path.dirname(os.path.abspath(__file__)) # app/services
        self.backend_dir = os.path.dirname(os.path.dirname(base_dir)) # backend
        self.sandbox_dir = os.path.join(self.backend_dir, "user_files", "pdf_uploads")
        
        if not os.path.exists(self.sandbox_dir):
            os.makedirs(self.sandbox_dir)

    def extract_text(self, filename: str) -> Optional[str]:
        """
        Extracts text from a PDF file located in the sandbox directory.
        """
        file_path = os.path.join(self.sandbox_dir, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return None

        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            return None

# Singleton instance
pdf_service = PDFService()
