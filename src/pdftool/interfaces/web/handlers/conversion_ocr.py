"""
Enhanced conversion service handler with OCR support
"""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from fastapi.responses import FileResponse

from ..interfaces import BaseServiceHandler
from ....common.models import ConversionOptions, ConversionFormat, OperationResult
from ....domains.document.operations.conversion_ocr import ConversionOperationOCR

logger = logging.getLogger(__name__)


class ConversionOCRServiceHandler(BaseServiceHandler):
    """Enhanced service handler for PDF conversion with OCR support"""

    @property
    def service_name(self) -> str:
        return "conversion_ocr"

    def __init__(self):
        super().__init__()
        self.operation = ConversionOperationOCR()

    async def handle(
        self,
        files: List[UploadFile],
        request: Optional[dict] = None,
        *args,
        **kwargs
    ) -> OperationResult:
        """Handle conversion request via standard interface"""
        if not files:
            raise ValueError("No files provided for conversion")

        file = files[0]  # Take first file
        format_type = request.get('format', 'txt') if request else 'txt'
        preserve_images = request.get('preserve_images', True) if request else True
        preserve_formatting = request.get('preserve_formatting', True) if request else True
        use_ocr = request.get('use_ocr', True) if request else True

        return await self.handle_conversion(
            file=file,
            format=format_type,
            preserve_images=preserve_images,
            preserve_formatting=preserve_formatting,
            use_ocr=use_ocr
        )

    async def handle_conversion(
        self,
        file: UploadFile,
        format: str,
        preserve_images: bool = True,
        preserve_formatting: bool = True,
        use_ocr: bool = True,
    ) -> OperationResult:
        """Handle PDF conversion with OCR support"""
        try:
            # Validate format
            try:
                format_enum = ConversionFormat(format.lower())
            except ValueError:
                return OperationResult(
                    success=False,
                    message=f"Unsupported format: {format}",
                    output_files=[],
                    details=f"Supported formats: {[f.value for f in ConversionFormat]}"
                )

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)

            try:
                # Create options
                options = ConversionOptions(
                    format=format_enum,
                    preserve_images=preserve_images,
                    preserve_formatting=preserve_formatting,
                    use_ocr=use_ocr
                )

                # Execute conversion
                result = self.operation.execute(temp_file_path, options)

                # Add OCR info to details
                if result.success and hasattr(result, 'details'):
                    if self.operation.ocr_enabled:
                        result.details += f" (OCR available)"
                    else:
                        result.details += f" (OCR not available - using text extraction only)"

                return result

            finally:
                # Clean up temporary file
                if temp_file_path.exists():
                    temp_file_path.unlink()

        except Exception as e:
            logger.error(f"OCR conversion failed: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Conversion failed: {str(e)}",
                output_files=[],
                details="Check server logs for more information"
            )

    def create_download_response(self, result: OperationResult, filename_prefix: str) -> FileResponse:
        """Create download response for converted file"""
        if not result.success or not result.output_files:
            raise ValueError("Cannot create download response for failed conversion")

        output_file = result.output_files[0]

        # Determine MIME type based on file extension
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html'
        }

        mime_type = mime_types.get(output_file.suffix, 'application/octet-stream')

        # Create download filename
        download_filename = f"{filename_prefix}{output_file.suffix}"

        return FileResponse(
            path=str(output_file),
            filename=download_filename,
            media_type=mime_type
        )

    def get_service_info(self) -> dict:
        """Get service information including OCR availability"""
        return {
            "name": "conversion_ocr",
            "description": "Enhanced PDF conversion with OCR support for scanned documents",
            "supported_formats": [f.value for f in ConversionFormat],
            "ocr_available": self.operation.ocr_enabled,
            "features": [
                "Text extraction from native PDFs",
                "OCR for scanned PDFs" if self.operation.ocr_enabled else "OCR not available",
                "Multiple output formats (TXT, Markdown, EPUB)",
                "Chinese and English text recognition" if self.operation.ocr_enabled else None
            ]
        }