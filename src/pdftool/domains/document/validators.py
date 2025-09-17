"""
文档域验证器

提供文档操作相关的验证逻辑。
"""

from pathlib import Path
from typing import List

from ...common.exceptions import PDFFileNotFoundError, PDFValidationError
from ...common.models import MergeOptions, SplitOptions, WatermarkOptions


def validate_document_files(files: List[Path]) -> None:
    """验证文档文件列表"""
    if not files:
        raise PDFValidationError("No files provided")

    for file_path in files:
        if not file_path.exists():
            raise PDFFileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise PDFValidationError(f"Not a PDF file: {file_path}")


def validate_merge_options(options: MergeOptions) -> None:
    """验证合并操作选项"""
    if hasattr(options, "output_filename") and not options.output_filename:
        raise PDFValidationError("Output filename cannot be empty")


def validate_split_options(options: SplitOptions) -> None:
    """验证拆分操作选项"""
    if options.mode == "page_range":
        if not options.start_page or not options.end_page:
            raise PDFValidationError("Start and end page required for page range split")
        if options.start_page > options.end_page:
            raise PDFValidationError("Start page cannot be greater than end page")


def validate_watermark_options(options: WatermarkOptions) -> None:
    """验证水印操作选项"""
    if not options.text and not options.image:
        raise PDFValidationError("Either text or image must be provided for watermark")

    if options.image and not Path(options.image).exists():
        raise PDFFileNotFoundError(f"Watermark image not found: {options.image}")
