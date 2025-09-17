"""
PDF split operation
"""

import logging
from pathlib import Path
from uuid import uuid4

import PyPDF2

from ..exceptions import PDFProcessingError, PDFValidationError
from ..interfaces import BasePDFOperation
from ..models import OperationResult, PageSelectionMode, PageSelectionOptions

logger = logging.getLogger(__name__)


class SplitOperation(BasePDFOperation):
    """PDF split operation implementation"""

    @property
    def operation_name(self) -> str:
        return "split"

    def validate_input(self, input_file: Path, options: PageSelectionOptions) -> None:
        """Validate split operation input"""
        self.validate_pdf_file(input_file)

    def execute(self, input_file: Path, options: PageSelectionOptions) -> OperationResult:
        """Execute PDF split operation"""
        self.validate_input(input_file, options)

        output_dir = options.output_dir or self.temp_dir / f"split_{uuid4().hex}"
        output_dir.mkdir(exist_ok=True)

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                output_files = []

                # Determine which pages to process
                if options.mode == PageSelectionMode.ALL_PAGES:
                    target_pages = list(range(1, total_pages + 1))
                elif options.mode in [
                    PageSelectionMode.SPECIFIC_PAGES,
                    PageSelectionMode.SINGLE_FILE,
                ]:
                    if not options.pages:
                        raise PDFValidationError("指定页面模式需要提供页面列表")
                    # Validate page range
                    for page_num in options.pages:
                        if page_num < 1 or page_num > total_pages:
                            raise PDFValidationError(f"页面 {page_num} 超出范围 (1-{total_pages})")
                    target_pages = options.pages
                else:
                    raise PDFValidationError(f"不支持的页面选择模式: {options.mode}")

                # Process pages based on mode
                if options.mode == PageSelectionMode.SINGLE_FILE:
                    # Merge selected pages into single file
                    writer = PyPDF2.PdfWriter()
                    for page_num in target_pages:
                        writer.add_page(reader.pages[page_num - 1])

                    if len(target_pages) == 1:
                        filename = f"{options.filename_prefix or input_file.stem}_page_{target_pages[0]}.pdf"
                    else:
                        filename = f"{options.filename_prefix or input_file.stem}_pages_{min(target_pages)}-{max(target_pages)}.pdf"

                    output_file = output_dir / filename
                    with open(output_file, "wb") as out_f:
                        writer.write(out_f)
                    output_files.append(output_file)

                else:
                    # Create separate file for each page
                    for page_num in target_pages:
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num - 1])

                        filename = (
                            f"{options.filename_prefix or input_file.stem}_page_{page_num}.pdf"
                        )
                        output_file = output_dir / filename

                        with open(output_file, "wb") as out_f:
                            writer.write(out_f)
                        output_files.append(output_file)

                pages_desc = (
                    f"{min(target_pages)}-{max(target_pages)}"
                    if len(target_pages) > 1
                    else str(target_pages[0])
                )
                logger.info(f"成功分割PDF页面: {pages_desc}")

                return OperationResult(
                    success=True,
                    message=f"成功处理 {len(target_pages)} 个页面: {pages_desc}",
                    output_files=output_files,
                    details=f"页面: {', '.join(map(str, target_pages))}",
                )

        except Exception as e:
            raise PDFProcessingError(f"Failed to split PDF: {str(e)}")
