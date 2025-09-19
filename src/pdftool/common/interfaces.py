"""
Core interfaces for PDF operations
"""

import logging
from pathlib import Path
from typing import Optional

import PyPDF2

from .exceptions import PDFFileNotFoundError, PDFValidationError

logger = logging.getLogger(__name__)


class BasePDFOperation:
    """Base class for PDF operations with common functionality"""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    def validate_pdf_file(self, file_path: Path) -> None:
        """Common PDF file validation"""
        if not file_path.exists():
            raise PDFFileNotFoundError(f"PDF file not found: {file_path}")

        if file_path.suffix.lower() != ".pdf":
            raise PDFValidationError(f"File is not a PDF: {file_path}")

        try:
            with open(file_path, "rb") as f:
                PyPDF2.PdfReader(f)
        except Exception as e:
            raise PDFValidationError(f"Invalid PDF file: {file_path}. Error: {str(e)}")

    def create_temp_file(self, suffix: str = "") -> Path:
        """Create a temporary file path"""
        from uuid import uuid4

        return self.temp_dir / f"temp_{uuid4().hex}{suffix}"

    def create_temp_dir(self) -> Path:
        """Create a temporary directory"""
        from uuid import uuid4

        temp_dir = self.temp_dir / f"temp_{uuid4().hex}"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
