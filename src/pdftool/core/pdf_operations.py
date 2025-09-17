"""
Core PDF operations module
"""

import io
import logging
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import PyPDF2
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .exceptions import PDFFileNotFoundError, PDFProcessingError, PDFValidationError
from .models import (
    ExtractOptions,
    MergeOptions,
    OperationResult,
    PageSelectionMode,
    PageSelectionOptions,
    PDFInfo,
    SplitMode,
    SplitOptions,
    WatermarkOptions,
    WatermarkPosition,
    WatermarkType,
)

logger = logging.getLogger(__name__)


class PDFOperations:
    """Core class for PDF operations"""

    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize PDF operations

        Args:
            temp_dir: Directory for temporary files. If None, uses system temp
        """
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    def validate_pdf_file(self, file_path: Path) -> None:
        """Validate that a file is a valid PDF"""
        if not file_path.exists():
            raise PDFFileNotFoundError(f"PDF file not found: {file_path}")

        if file_path.suffix.lower() != ".pdf":
            raise PDFValidationError(f"File is not a PDF: {file_path}")

        try:
            with open(file_path, "rb") as f:
                PyPDF2.PdfReader(f)
        except Exception as e:
            raise PDFValidationError(f"Invalid PDF file: {file_path}. Error: {str(e)}")

    def get_pdf_info(self, file_path: Path) -> PDFInfo:
        """Get information about a PDF file"""
        self.validate_pdf_file(file_path)

        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                info = PDFInfo(
                    pages=len(reader.pages), file_path=file_path, file_size=file_path.stat().st_size
                )

                if reader.metadata:
                    info.title = reader.metadata.title
                    info.author = reader.metadata.author
                    info.creation_date = reader.metadata.creation_date

                return info

        except Exception as e:
            raise PDFProcessingError(f"Failed to read PDF info: {str(e)}")

    def merge_pdfs(
        self, input_files: List[Path], options: Optional[MergeOptions] = None
    ) -> OperationResult:
        """Merge multiple PDF files into one"""
        if len(input_files) < 2:
            raise PDFValidationError("At least 2 PDF files are required for merging")

        for file_path in input_files:
            self.validate_pdf_file(file_path)

        options = options or MergeOptions()
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

    def split_pdf(self, input_file: Path, options: SplitOptions) -> OperationResult:
        """Split a PDF file according to specified options"""
        self.validate_pdf_file(input_file)

        output_dir = options.output_dir or self.temp_dir / f"split_{uuid4().hex}"
        output_dir.mkdir(exist_ok=True)

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                output_files = []

                if options.mode == SplitMode.ALL_PAGES:
                    for page_num in range(total_pages):
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num])

                        filename = (
                            f"{options.filename_prefix or input_file.stem}_page_{page_num + 1}.pdf"
                        )
                        output_file = output_dir / filename

                        with open(output_file, "wb") as out_f:
                            writer.write(out_f)

                        output_files.append(output_file)

                elif (
                    options.mode == SplitMode.SPECIFIC_PAGES
                    and options.start_page
                    and options.end_page
                ):
                    # Handle page range mode using start_page and end_page
                    start = (options.start_page or 1) - 1
                    end = options.end_page or total_pages

                    if start < 0 or end > total_pages or start >= end:
                        raise PDFValidationError("Invalid page range")

                    writer = PyPDF2.PdfWriter()
                    for page_num in range(start, end):
                        writer.add_page(reader.pages[page_num])

                    filename = (
                        f"{options.filename_prefix or input_file.stem}_pages_{start + 1}-{end}.pdf"
                    )
                    output_file = output_dir / filename

                    with open(output_file, "wb") as out_f:
                        writer.write(out_f)

                    output_files.append(output_file)

                logger.info(f"Successfully split PDF into {len(output_files)} files")
                return OperationResult(
                    success=True,
                    message=f"Successfully split PDF into {len(output_files)} files",
                    output_files=output_files,
                )

        except PDFValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise PDFProcessingError(f"Failed to split PDF: {str(e)}")

    def extract_pages(self, input_file: Path, options: ExtractOptions) -> OperationResult:
        """Extract specific pages from a PDF file"""
        self.validate_pdf_file(input_file)

        if not options.pages:
            raise PDFValidationError("至少需要指定一个要提取的页面")

        output_dir = options.output_dir or self.temp_dir / f"extract_{uuid4().hex}"
        output_dir.mkdir(exist_ok=True)

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                output_files = []

                # 验证页面范围
                for page_num in options.pages:
                    if page_num < 1 or page_num > total_pages:
                        raise PDFValidationError(f"页面 {page_num} 超出范围 (1-{total_pages})")

                # 根据页面数量决定输出方式
                if len(options.pages) == 1:
                    # 单页提取 - 直接输出PDF文件
                    page_num = options.pages[0]
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])

                    filename = f"{options.filename_prefix or input_file.stem}_page_{page_num}.pdf"
                    output_file = output_dir / filename

                    with open(output_file, "wb") as out_f:
                        writer.write(out_f)

                    output_files.append(output_file)

                else:
                    # 多页提取 - 每页单独文件
                    for page_num in options.pages:
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num - 1])

                        filename = (
                            f"{options.filename_prefix or input_file.stem}_page_{page_num}.pdf"
                        )
                        output_file = output_dir / filename

                        with open(output_file, "wb") as out_f:
                            writer.write(out_f)

                        output_files.append(output_file)

                extracted_pages = ", ".join(map(str, options.pages))
                logger.info(f"Successfully extracted pages [{extracted_pages}] from PDF")

                return OperationResult(
                    success=True,
                    message=f"成功提取 {len(options.pages)} 个页面: {extracted_pages}",
                    output_files=output_files,
                    details=f"提取的页面: {extracted_pages}",
                )

        except Exception as e:
            raise PDFProcessingError(f"Failed to extract pages: {str(e)}")

    def select_pages(self, input_file: Path, options: PageSelectionOptions) -> OperationResult:
        """统一的PDF页面选择方法，支持多种模式"""
        self.validate_pdf_file(input_file)

        output_dir = options.output_dir or self.temp_dir / f"select_{uuid4().hex}"
        output_dir.mkdir(exist_ok=True)

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                output_files = []

                # 根据模式确定要处理的页面
                if options.mode == PageSelectionMode.ALL_PAGES:
                    target_pages = list(range(1, total_pages + 1))
                elif options.mode in [
                    PageSelectionMode.SPECIFIC_PAGES,
                    PageSelectionMode.SINGLE_FILE,
                ]:
                    if not options.pages:
                        raise PDFValidationError("指定页面模式需要提供页面列表")
                    # 验证页面范围
                    for page_num in options.pages:
                        if page_num < 1 or page_num > total_pages:
                            raise PDFValidationError(f"页面 {page_num} 超出范围 (1-{total_pages})")
                    target_pages = options.pages
                else:
                    raise PDFValidationError(f"不支持的页面选择模式: {options.mode}")

                # 根据模式决定输出方式
                if options.mode == PageSelectionMode.SINGLE_FILE:
                    # 合并为单个文件
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
                    # 每页单独文件
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
                logger.info(f"成功选择PDF页面: {pages_desc}")

                return OperationResult(
                    success=True,
                    message=f"成功处理 {len(target_pages)} 个页面: {pages_desc}",
                    output_files=output_files,
                    details=f"页面: {', '.join(map(str, target_pages))}",
                )

        except Exception as e:
            raise PDFProcessingError(f"Failed to select pages: {str(e)}")

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

    def add_watermark(self, input_file: Path, options: WatermarkOptions) -> OperationResult:
        """Add watermark to PDF"""
        self.validate_pdf_file(input_file)

        output_file = options.output_file or self.temp_dir / f"watermarked_{uuid4().hex}.pdf"

        try:
            # Create watermark PDF
            watermark_pdf = self._create_watermark_pdf(options)

            # Apply watermark to input PDF
            with open(input_file, "rb") as input_pdf_file:
                input_pdf = PyPDF2.PdfReader(input_pdf_file)
                output_pdf = PyPDF2.PdfWriter()

                # Get watermark reader
                watermark_reader = PyPDF2.PdfReader(watermark_pdf)
                watermark_page = watermark_reader.pages[0]

                total_pages = len(input_pdf.pages)

                # Determine which pages to watermark
                if options.page_selection == PageSelectionMode.ALL_PAGES:
                    target_pages = list(range(total_pages))
                elif options.page_selection == PageSelectionMode.SPECIFIC_PAGES:
                    if not options.specific_pages:
                        raise PDFValidationError("指定页面模式需要提供页面列表")
                    # Convert 1-based to 0-based indexing
                    target_pages = [p - 1 for p in options.specific_pages if 0 < p <= total_pages]
                else:
                    # Default to all pages
                    target_pages = list(range(total_pages))

                # Process each page
                for i, page in enumerate(input_pdf.pages):
                    if i in target_pages:
                        # Merge page with watermark
                        page.merge_page(watermark_page)
                    output_pdf.add_page(page)

                # Write output file
                with open(output_file, "wb") as output_file_obj:
                    output_pdf.write(output_file_obj)

            logger.info(f"Successfully added watermark to PDF: {input_file}")
            return OperationResult(
                success=True,
                message=f"成功添加水印到 {len(target_pages)} 个页面",
                output_files=[output_file],
                details=f"水印类型: {options.watermark_type.value}, 位置: {options.position.value}",
            )

        except Exception as e:
            raise PDFProcessingError(f"Failed to add watermark: {str(e)}")
        finally:
            # Clean up temporary watermark file
            try:
                if "watermark_pdf" in locals():
                    watermark_pdf.close()
            except:
                pass

    def _create_watermark_pdf(self, options: WatermarkOptions) -> io.BytesIO:
        """Create a transparent watermark PDF"""
        watermark_buffer = io.BytesIO()

        # Create canvas with letter size (can be adjusted based on input PDF)
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        page_width, page_height = letter

        # Set transparency
        c.setFillAlpha(options.opacity)

        if options.watermark_type == WatermarkType.TEXT:
            self._add_text_watermark(c, options, page_width, page_height)
        elif options.watermark_type == WatermarkType.IMAGE:
            self._add_image_watermark(c, options, page_width, page_height)

        c.save()
        watermark_buffer.seek(0)
        return watermark_buffer

    def _add_text_watermark(
        self,
        canvas_obj: canvas.Canvas,
        options: WatermarkOptions,
        page_width: float,
        page_height: float,
    ) -> None:
        """Add text watermark to canvas"""
        if not options.text:
            raise PDFValidationError("文本水印需要提供文本内容")

        # Set font and size
        font_size = options.font_size or 36
        canvas_obj.setFont("Helvetica", font_size)

        # Set color
        if options.font_color:
            # Convert hex color to RGB
            color_hex = options.font_color.lstrip("#")
            if len(color_hex) == 6:
                r = int(color_hex[0:2], 16) / 255.0
                g = int(color_hex[2:4], 16) / 255.0
                b = int(color_hex[4:6], 16) / 255.0
                canvas_obj.setFillColor(colors.Color(r, g, b))
            else:
                canvas_obj.setFillColor(colors.black)
        else:
            canvas_obj.setFillColor(colors.black)

        # Calculate position
        text_width = canvas_obj.stringWidth(options.text, "Helvetica", font_size)
        x, y = self._calculate_position(
            options.position, page_width, page_height, text_width, font_size
        )

        # Draw text
        canvas_obj.drawString(x, y, options.text)

    def _add_image_watermark(
        self,
        canvas_obj: canvas.Canvas,
        options: WatermarkOptions,
        page_width: float,
        page_height: float,
    ) -> None:
        """Add image watermark to canvas"""
        if not options.image_path or not options.image_path.exists():
            raise PDFValidationError("图片水印需要提供有效的图片文件")

        try:
            # Open and process image
            img = Image.open(options.image_path)
            img_width, img_height = img.size

            # Apply scaling
            scale = (options.image_scale or 100) / 100.0
            scaled_width = img_width * scale
            scaled_height = img_height * scale

            # Calculate position
            x, y = self._calculate_position(
                options.position, page_width, page_height, scaled_width, scaled_height
            )

            # Draw image
            canvas_obj.drawImage(
                str(options.image_path), x, y, width=scaled_width, height=scaled_height, mask="auto"
            )

        except Exception as e:
            raise PDFProcessingError(f"Failed to process watermark image: {str(e)}")

    def _calculate_position(
        self,
        position: WatermarkPosition,
        page_width: float,
        page_height: float,
        element_width: float,
        element_height: float,
    ) -> tuple[float, float]:
        """Calculate watermark position coordinates"""
        margin = 50  # Margin from edges

        # Calculate x coordinate
        if position in [
            WatermarkPosition.TOP_LEFT,
            WatermarkPosition.CENTER_LEFT,
            WatermarkPosition.BOTTOM_LEFT,
        ]:
            x = margin
        elif position in [
            WatermarkPosition.TOP_CENTER,
            WatermarkPosition.CENTER,
            WatermarkPosition.BOTTOM_CENTER,
        ]:
            x = (page_width - element_width) / 2
        else:  # RIGHT positions
            x = page_width - element_width - margin

        # Calculate y coordinate
        if position in [
            WatermarkPosition.TOP_LEFT,
            WatermarkPosition.TOP_CENTER,
            WatermarkPosition.TOP_RIGHT,
        ]:
            y = page_height - element_height - margin
        elif position in [
            WatermarkPosition.CENTER_LEFT,
            WatermarkPosition.CENTER,
            WatermarkPosition.CENTER_RIGHT,
        ]:
            y = (page_height - element_height) / 2
        else:  # BOTTOM positions
            y = margin

        return x, y

    def cleanup_temp_files(self, files: List[Path]) -> None:
        """Clean up temporary files"""
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {str(e)}")
