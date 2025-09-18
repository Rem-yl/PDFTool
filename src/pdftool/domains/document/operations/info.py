"""
PDF info operation
"""

import logging
from pathlib import Path

import PyPDF2

from ....common.exceptions import PDFProcessingError
from ....common.interfaces import BasePDFOperation
from ....common.models import PDFInfo

logger = logging.getLogger(__name__)


class InfoOperation(BasePDFOperation):
    """PDF info operation implementation"""

    @property
    def operation_name(self) -> str:
        return "info"

    def validate_input(self, input_file: Path, options: None = None) -> None:
        """Validate info operation input"""
        self.validate_pdf_file(input_file)

    def execute(self, input_file: Path, options: None = None) -> PDFInfo:
        """Execute PDF info operation"""
        self.validate_input(input_file, options)

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                info = PDFInfo(
                    pages=len(reader.pages),
                    file_path=input_file,
                    file_size=input_file.stat().st_size,
                )

                if reader.metadata:
                    info.title = reader.metadata.title
                    info.author = reader.metadata.author
                    info.creation_date = reader.metadata.creation_date

                return info

        except Exception as e:
            raise PDFProcessingError(f"Failed to read PDF info: {str(e)}")
