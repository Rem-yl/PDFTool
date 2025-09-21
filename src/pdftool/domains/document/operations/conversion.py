"""
Simplified PDF conversion operations without external dependencies
"""

import logging
from pathlib import Path
from typing import List, Optional

import PyPDF2

from ....common.exceptions import PDFProcessingError
from ....common.interfaces import BasePDFOperation
from ....common.models import ConversionFormat, ConversionOptions, OperationResult

logger = logging.getLogger(__name__)


class ConversionOperation(BasePDFOperation):
    """PDF conversion operation for web frontend"""

    @property
    def operation_name(self) -> str:
        return "conversion"

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
        """Execute PDF conversion operation"""
        self.validate_input(input_file, options)

        try:
            if options.format == ConversionFormat.TXT:
                return self._convert_to_txt_simple(input_file, options)
            elif options.format == ConversionFormat.MARKDOWN:
                return self._convert_to_markdown_simple(input_file, options)
            elif options.format == ConversionFormat.EPUB:
                return self._convert_to_epub_simple(input_file, options)
            else:
                raise PDFProcessingError(f"Unsupported format: {options.format}")

        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise PDFProcessingError(f"Failed to convert PDF: {str(e)}")

    def _extract_text_simple(self, input_file: Path) -> List[str]:
        """Extract text using PyPDF2 with enhanced scanned PDF detection"""
        pages_text = []
        total_chars = 0
        pages_with_text = 0

        with open(input_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text().strip()

                    if text:
                        pages_text.append(text)
                        total_chars += len(text)
                        pages_with_text += 1
                    else:
                        # Analyze page content for scanned PDF detection
                        page_info = self._analyze_page_structure(page, page_num)
                        pages_text.append(f"[Page {page_num} - Scanned content detected]\n{page_info}")

                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    pages_text.append(f"[Page {page_num} - Extraction failed: {e}]")

            # Add comprehensive document analysis
            if total_pages > 0:
                text_coverage = (pages_with_text / total_pages) * 100
                analysis = f"\n=== 📊 Document Analysis Report ===\n"
                analysis += f"📄 Total pages: {total_pages}\n"
                analysis += f"✅ Pages with text: {pages_with_text} ({text_coverage:.1f}%)\n"
                analysis += f"📝 Total characters: {total_chars:,}\n"

                if text_coverage < 10:
                    analysis += f"\n🔍 Analysis: This appears to be a scanned document (image-based PDF).\n"
                    analysis += f"💡 Recommendation: For text extraction from scanned documents, OCR tools are required.\n"
                    analysis += f"🛠️  Alternative solutions:\n"
                    analysis += f"   • Use Adobe Acrobat Pro with OCR\n"
                    analysis += f"   • Try online OCR services\n"
                    analysis += f"   • Install Tesseract OCR for this system\n"
                elif text_coverage < 50:
                    analysis += f"\n⚠️  Note: Mixed content detected - some pages may be scanned.\n"
                else:
                    analysis += f"\n✅ Good text extraction - this appears to be a text-based PDF.\n"

                pages_text.insert(0, analysis)

        return pages_text

    def _analyze_page_structure(self, page, page_num: int) -> str:
        """Analyze page structure to provide useful information"""
        info = []

        try:
            # Check for images/XObjects
            if '/Resources' in page:
                resources = page['/Resources']
                if '/XObject' in resources:
                    xobjects = resources['/XObject']
                    image_count = 0
                    for obj_name, obj in xobjects.items():
                        if hasattr(obj, 'get') and obj.get('/Subtype') == '/Image':
                            image_count += 1
                    if image_count > 0:
                        info.append(f"• Contains {image_count} image(s)")

            # Page dimensions
            if hasattr(page, 'mediabox'):
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                info.append(f"• Page size: {width:.0f} × {height:.0f} points")

            # Check for fonts (indicates potential text)
            if '/Resources' in page and '/Font' in page['/Resources']:
                fonts = page['/Resources']['/Font']
                info.append(f"• Contains {len(fonts)} font(s) but no extractable text")

            if not info:
                info.append("• Likely contains scanned image content")

        except Exception as e:
            info.append(f"• Analysis error: {str(e)}")

        return "\n".join(info)

    def _convert_to_txt_simple(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to plain text using PyPDF2"""
        output_file = options.output_file or self.create_temp_file(".txt")

        pages_text = self._extract_text_simple(input_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            for i, text in enumerate(pages_text, 1):
                f.write(f"=== Page {i} ===\n\n")
                f.write(text)
                f.write("\n\n")

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to TXT",
            output_files=[output_file],
            details=f"Converted {len(pages_text)} pages"
        )

    def _convert_to_markdown_simple(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to Markdown using basic text processing"""
        output_file = options.output_file or self.create_temp_file(".md")

        pages_text = self._extract_text_simple(input_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            # Add document title
            f.write(f"# {input_file.stem}\n\n")

            for i, text in enumerate(pages_text, 1):
                f.write(f"## Page {i}\n\n")

                if text:
                    # Simple markdown formatting
                    lines = text.split('\n')
                    processed_lines = []

                    for line in lines:
                        line = line.strip()
                        if not line:
                            processed_lines.append("")
                            continue

                        # Detect potential headers (all caps, short lines)
                        if (len(line) < 60 and
                            line.isupper() and
                            not line.endswith('.') and
                            len(line.split()) <= 8):
                            processed_lines.append(f"### {line.title()}")
                        else:
                            processed_lines.append(line)

                    f.write('\n'.join(processed_lines))
                    f.write("\n\n")

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to Markdown",
            output_files=[output_file],
            details=f"Converted {len(pages_text)} pages"
        )

    def _convert_to_epub_simple(
        self, input_file: Path, options: ConversionOptions
    ) -> OperationResult:
        """Convert PDF to EPUB using basic HTML structure"""
        output_file = options.output_file or self.create_temp_file(".epub")

        # For now, create a simple HTML file instead of true EPUB
        # This is a placeholder implementation
        html_output = output_file.with_suffix('.html')

        pages_text = self._extract_text_simple(input_file)

        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{input_file.stem}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; }}
        .page {{ margin-bottom: 40px; page-break-after: always; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>{input_file.stem}</h1>
""")

            for i, text in enumerate(pages_text, 1):
                f.write(f'    <div class="page">\n')
                f.write(f'        <h2>Page {i}</h2>\n')
                f.write(f'        <pre>{text}</pre>\n')
                f.write(f'    </div>\n')

            f.write("</body>\n</html>")

        return OperationResult(
            success=True,
            message=f"PDF successfully converted to HTML (EPUB placeholder)",
            output_files=[html_output],
            details=f"Converted {len(pages_text)} pages to HTML format"
        )