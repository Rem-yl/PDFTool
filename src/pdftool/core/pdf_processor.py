"""
PDF Processor - New extensible architecture using strategy pattern
"""

import shutil
import zipfile
from pathlib import Path
from typing import Any, List, Optional, Union
from uuid import uuid4

from .exceptions import PDFProcessingError
from .interfaces import IPDFOperation
from .models import OperationResult, PDFInfo
from .operation_factory import PDFOperationFactory


class PDFProcessor:
    """
    New extensible PDF processor using strategy pattern.
    Delegates operations to specific operation classes.
    """

    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize PDF processor

        Args:
            temp_dir: Directory for temporary files. If None, uses system temp
        """
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        self.operation_factory = PDFOperationFactory(temp_dir=self.temp_dir)

    def execute_operation(self, operation_type: str, input_data: Any, options: Any) -> Any:
        """
        Execute a PDF operation using the strategy pattern

        Args:
            operation_type: Type of operation (merge, split, watermark, etc.)
            input_data: Input data for the operation (file path, list of paths, etc.)
            options: Operation-specific options

        Returns:
            Operation result
        """
        try:
            operation = self.operation_factory.create_operation(operation_type)
            return operation.execute(input_data, options)
        except ValueError as e:
            raise PDFProcessingError(f"Unknown operation: {operation_type}")

    def get_available_operations(self) -> list[str]:
        """Get list of available operations"""
        return self.operation_factory.list_operations()

    def register_operation(self, operation_type: str, operation_class: type) -> None:
        """Register a new operation type"""
        self.operation_factory.register_operation(operation_type, operation_class)

    # Convenience methods that delegate to specific operations
    def merge_pdfs(self, input_files: List[Path], options: Any) -> OperationResult:
        """Merge multiple PDF files"""
        return self.execute_operation("merge", input_files, options)

    def split_pdf(self, input_file: Path, options: Any) -> OperationResult:
        """Split a PDF file"""
        return self.execute_operation("split", input_file, options)

    def add_watermark(self, input_file: Path, options: Any) -> OperationResult:
        """Add watermark to PDF"""
        return self.execute_operation("watermark", input_file, options)

    def get_pdf_info(self, input_file: Path) -> PDFInfo:
        """Get PDF information"""
        return self.execute_operation("info", input_file, None)

    # Utility methods (kept for backward compatibility)
    def create_zip_archive(self, files: List[Path], output_path: Optional[Path] = None) -> Path:
        """Create a ZIP archive from a list of files"""
        output_path = output_path or self.temp_dir / f"archive_{uuid4().hex}.zip"

        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    zf.write(file_path, file_path.name)

            return output_path

        except Exception as e:
            raise PDFProcessingError(f"Failed to create ZIP archive: {str(e)}")

    def cleanup_temp_files(self, files: List[Path]) -> None:
        """Clean up temporary files"""
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                # Use logging instead of print for production
                pass
