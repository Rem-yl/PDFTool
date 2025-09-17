"""
Core interfaces for PDF operations
"""

import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional

import PyPDF2

from .exceptions import PDFFileNotFoundError, PDFValidationError
from .models import OperationResult

logger = logging.getLogger(__name__)


class IPDFOperation(ABC):
    """Base interface for all PDF operations"""

    @abstractmethod
    def execute(self, input_data: Any, options: Any) -> Any:
        """Execute the PDF operation"""
        pass

    @property
    @abstractmethod
    def operation_name(self) -> str:
        """Get operation name for registration"""
        pass


class IPDFOperationFactory(ABC):
    """Factory interface for creating PDF operations"""

    @abstractmethod
    def create_operation(self, operation_type: str) -> IPDFOperation:
        """Create a specific PDF operation"""
        pass

    @abstractmethod
    def register_operation(self, operation_type: str, operation_class: type) -> None:
        """Register a new operation type"""
        pass

    @abstractmethod
    def list_operations(self) -> list[str]:
        """List all available operation types"""
        pass


class BasePDFOperation(IPDFOperation):
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

    def cleanup_temp_files(self, files: List[Path]) -> None:
        """Common cleanup functionality"""
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {str(e)}")

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
