"""
PDF merge operation
"""

import logging
from pathlib import Path
from typing import List
from uuid import uuid4

import PyPDF2

from ..exceptions import PDFProcessingError, PDFValidationError
from ..interfaces import BasePDFOperation
from ..models import MergeOptions, OperationResult

logger = logging.getLogger(__name__)


class MergeOperation(BasePDFOperation):
    """PDF merge operation implementation"""

    @property
    def operation_name(self) -> str:
        return "merge"

    def validate_input(self, input_files: List[Path], options: MergeOptions) -> None:
        """Validate merge operation input"""
        if not isinstance(input_files, list) or len(input_files) < 2:
            raise PDFValidationError("At least 2 PDF files are required for merging")

        for file_path in input_files:
            self.validate_pdf_file(file_path)

    def execute(self, input_files: List[Path], options: MergeOptions) -> OperationResult:
        """Execute PDF merge operation"""
        self.validate_input(input_files, options)

        output_file = options.output_file or self.temp_dir / f"merged_{uuid4().hex}.pdf"

        try:
            merger = PyPDF2.PdfMerger()

            for file_path in input_files:
                merger.append(str(file_path))

            with open(output_file, "wb") as f:
                merger.write(f)

            merger.close()

            logger.info(f"Successfully merged {len(input_files)} PDFs into {output_file}")
            return OperationResult(
                success=True,
                message=f"Successfully merged {len(input_files)} PDF files",
                output_files=[output_file],
            )

        except Exception as e:
            raise PDFProcessingError(f"Failed to merge PDFs: {str(e)}")
