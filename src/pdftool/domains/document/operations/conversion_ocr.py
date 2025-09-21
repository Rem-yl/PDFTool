"""
Enhanced PDF conversion operations with OCR support for scanned PDFs
"""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

import PyPDF2

from ....common.exceptions import PDFProcessingError
from ....common.interfaces import BasePDFOperation
from ....common.models import ConversionFormat, ConversionOptions, OperationResult

logger = logging.getLogger(__name__)

# Try to import OCR dependencies, fall back gracefully if not available
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
    logger.info("OCR dependencies loaded successfully")
except (ImportError, OSError) as e:
    OCR_AVAILABLE = False
    logger.warning(f"OCR dependencies not available: {e}")
    # Disable PIL import to avoid GLIBCXX issues
    pytesseract = None
    convert_from_path = None


class ConversionOperationOCR(BasePDFOperation):
    """Enhanced PDF conversion operation with OCR support"""

    @property
    def operation_name(self) -> str:
        return "conversion_ocr"

    def __init__(self):
        super().__init__()
        self.ocr_enabled = OCR_AVAILABLE

    def validate_input(
        self, input_file: Path, options: ConversionOptions
    ) -> None:
        """Validate conversion operation input"""
        self.validate_pdf_file(input_file)
        if not options or not options.format:
            raise PDFProcessingError("Conversion format must be specified")

    def execute(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Execute PDF conversion operation with OCR fallback"""
        self.validate_input(input_file, options)

        try:
            if options.format == ConversionFormat.TXT:
                return self._convert_to_txt_enhanced(input_file, options)
            elif options.format == ConversionFormat.MARKDOWN:
                return self._convert_to_markdown_enhanced(input_file, options)
            elif options.format == ConversionFormat.EPUB:
                return self._convert_to_epub_enhanced(input_file, options)
            else:
                raise PDFProcessingError(f"Unsupported format: {options.format}")

        except Exception as e:
            logger.error(f"Enhanced PDF conversion failed: {str(e)}")
            raise PDFProcessingError(f"Conversion failed: {str(e)}")

    def _extract_text_enhanced(self, input_file: Path, use_ocr_fallback: bool = True) -> List[str]:
        """Extract text with enhanced analysis for scanned pages"""
        pages_text = []
        total_chars = 0
        pages_with_text = 0

        # First try regular text extraction
        with open(input_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text().strip()

                    if text:
                        pages_text.append(text)
                        total_chars += len(text)
                        pages_with_text += 1
                    else:
                        # Enhanced analysis for scanned pages
                        page_analysis = self._analyze_page_content(page, page_num)

                        # If OCR is available and enabled, try OCR
                        if self.ocr_enabled and use_ocr_fallback:
                            logger.info(f"No text found on page {page_num}, attempting OCR...")
                            ocr_text = self._ocr_page(input_file, page_num)
                            if ocr_text:
                                pages_text.append(f"[OCR] {ocr_text}")
                                total_chars += len(ocr_text)
                                pages_with_text += 1
                            else:
                                pages_text.append(f"[Page {page_num} - Scanned content detected, OCR failed]\n{page_analysis}")
                        else:
                            pages_text.append(f"[Page {page_num} - Scanned content detected, OCR not available]\n{page_analysis}")

                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    pages_text.append(f"[Page {page_num} - Extraction failed: {e}]")

            # Add document analysis summary
            if total_pages > 0:
                text_coverage = (pages_with_text / total_pages) * 100
                summary = f"\n=== Document Analysis ===\n"
                summary += f"Total pages: {total_pages}\n"
                summary += f"Pages with extractable text: {pages_with_text} ({text_coverage:.1f}%)\n"
                summary += f"Total characters extracted: {total_chars}\n"

                if text_coverage < 10:
                    summary += f"Note: This appears to be a scanned document. "
                    if self.ocr_enabled:
                        summary += "OCR processing has been attempted."
                    else:
                        summary += "For better results, install Tesseract OCR support."

                pages_text.insert(0, summary)

        return pages_text

    def _analyze_page_content(self, page, page_num: int) -> str:
        """Analyze page content to provide useful information about scanned pages"""
        analysis = []

        try:
            # Check for images
            if hasattr(page, 'images') and page.images:
                analysis.append(f"• Contains {len(page.images)} image(s)")
            elif '/XObject' in page.get('/Resources', {}):
                xobjects = page['/Resources']['/XObject']
                image_count = sum(1 for obj in xobjects.values()
                                if hasattr(obj, 'get') and obj.get('/Subtype') == '/Image')
                if image_count > 0:
                    analysis.append(f"• Contains {image_count} embedded image(s)")

            # Check page dimensions
            if hasattr(page, 'mediabox'):
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                analysis.append(f"• Page size: {width:.0f} x {height:.0f} points")

            # Check for annotations
            if '/Annots' in page:
                analysis.append(f"• Contains annotations or form fields")

            if not analysis:
                analysis.append("• Likely contains scanned image content")

        except Exception as e:
            analysis.append(f"• Content analysis failed: {str(e)}")

        return "\n".join(analysis)

    def _ocr_page(self, pdf_file: Path, page_number: int) -> Optional[str]:
        """Extract text from a specific page using OCR"""
        if not self.ocr_enabled:
            return None

        try:
            # Convert specific page to image
            images = convert_from_path(
                pdf_file,
                first_page=page_number,
                last_page=page_number,
                dpi=200  # Good balance between quality and speed
            )

            if not images:
                return None

            # Extract text using OCR
            text = pytesseract.image_to_string(
                images[0],
                lang='eng+chi_sim',  # Support English and Simplified Chinese
                config='--psm 3'     # Fully automatic page segmentation
            )

            return text.strip() if text.strip() else None

        except Exception as e:
            logger.warning(f"OCR failed for page {page_number}: {e}")
            return None

    def _convert_to_txt_enhanced(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to plain text with OCR support"""
        output_file = options.output_file or self.create_temp_file(".txt")

        pages_text = self._extract_text_enhanced(input_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            for i, text in enumerate(pages_text, 1):
                f.write(f"=== Page {i} ===\n\n")
                f.write(text)
                f.write("\n\n")

        ocr_pages = sum(1 for text in pages_text if text.startswith("[OCR]"))
        details = f"Converted {len(pages_text)} pages"
        if ocr_pages > 0:
            details += f" ({ocr_pages} pages processed with OCR)"

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to TXT",
            output_files=[output_file],
            details=details
        )

    def _convert_to_markdown_enhanced(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to Markdown with OCR support"""
        output_file = options.output_file or self.create_temp_file(".md")

        pages_text = self._extract_text_enhanced(input_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            # Generate title from filename
            title = input_file.stem.replace('_', ' ').title()
            f.write(f"# {title}\n\n")

            for i, text in enumerate(pages_text, 1):
                f.write(f"## Page {i}\n\n")

                # Simple processing to detect potential headings
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        f.write("\n")
                        continue

                    # Detect potential headings (short lines, all caps, etc.)
                    if len(line) < 60 and (line.isupper() or line.istitle()):
                        f.write(f"### {line}\n\n")
                    else:
                        f.write(f"{line}\n")

                f.write("\n---\n\n")

        ocr_pages = sum(1 for text in pages_text if text.startswith("[OCR]"))
        details = f"Converted {len(pages_text)} pages to Markdown"
        if ocr_pages > 0:
            details += f" ({ocr_pages} pages processed with OCR)"

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to Markdown",
            output_files=[output_file],
            details=details
        )

    def _convert_to_epub_enhanced(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to EPUB HTML format with OCR support"""
        output_file = options.output_file or self.create_temp_file(".html")

        pages_text = self._extract_text_enhanced(input_file)

        title = input_file.stem.replace('_', ' ').title()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; }}
        .page {{ margin-bottom: 40px; page-break-after: always; }}
        .ocr-content {{ background-color: #f9f9f9; padding: 10px; border-left: 3px solid #007acc; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
""")

            for i, text in enumerate(pages_text, 1):
                is_ocr = text.startswith("[OCR]")
                if is_ocr:
                    text = text[5:]  # Remove [OCR] prefix
                    f.write(f'    <div class="page ocr-content">\n')
                    f.write(f'        <h2>Page {i} (OCR)</h2>\n')
                else:
                    f.write(f'    <div class="page">\n')
                    f.write(f'        <h2>Page {i}</h2>\n')

                f.write(f'        <pre>{text}</pre>\n')
                f.write(f'    </div>\n\n')

            f.write('</body>\n</html>')

        ocr_pages = sum(1 for text in pages_text if text.startswith("[OCR]"))
        details = f"Converted {len(pages_text)} pages to EPUB HTML"
        if ocr_pages > 0:
            details += f" ({ocr_pages} pages processed with OCR)"

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to EPUB HTML",
            output_files=[output_file],
            details=details
        )