"""
Core interfaces for PDF operations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from .models import OperationResult


class IPDFOperation(ABC):
    """Base interface for all PDF operations"""

    @abstractmethod
    def execute(self, input_file: Path, options: Any) -> OperationResult:
        """Execute the PDF operation"""
        pass

    @abstractmethod
    def validate_input(self, input_file: Path, options: Any) -> None:
        """Validate input parameters"""
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
        from .pdf_operations import (
            PDFOperations,  # Import here to avoid circular imports
        )

        # Use existing validation logic
        pdf_ops = PDFOperations(self.temp_dir)
        pdf_ops.validate_pdf_file(file_path)

    def cleanup_temp_files(self, files: list[Path]) -> None:
        """Common cleanup functionality"""
        from .pdf_operations import PDFOperations

        pdf_ops = PDFOperations(self.temp_dir)
        pdf_ops.cleanup_temp_files(files)
