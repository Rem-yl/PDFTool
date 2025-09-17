"""
PDF watermark operation
"""

import io
import logging
from pathlib import Path
from uuid import uuid4

import PyPDF2
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ....common.exceptions import PDFProcessingError, PDFValidationError
from ....common.interfaces import BasePDFOperation
from ....common.models import (
    OperationResult,
    PageSelectionMode,
    WatermarkOptions,
    WatermarkPosition,
    WatermarkType,
)

logger = logging.getLogger(__name__)


class WatermarkOperation(BasePDFOperation):
    """PDF watermark operation implementation"""

    @property
    def operation_name(self) -> str:
        return "watermark"

    def validate_input(self, input_file: Path, options: WatermarkOptions) -> None:
        """Validate watermark operation input"""
        self.validate_pdf_file(input_file)

        if options.watermark_type == WatermarkType.TEXT and not options.text:
            raise PDFValidationError("文本水印需要提供文本内容")

        if options.watermark_type == WatermarkType.IMAGE:
            if not options.image_path or not options.image_path.exists():
                raise PDFValidationError("图片水印需要提供有效的图片文件")

    def execute(self, input_file: Path, options: WatermarkOptions) -> OperationResult:
        """Execute PDF watermark operation"""
        self.validate_input(input_file, options)

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
