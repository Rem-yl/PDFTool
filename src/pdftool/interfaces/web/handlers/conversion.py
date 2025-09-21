"""
PDF conversion service handler
"""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile

from ....common.models import ConversionFormat, ConversionOptions, OperationResult
from ....domains.document.operations.conversion import ConversionOperation
from ..interfaces import BaseServiceHandler

logger = logging.getLogger(__name__)


class ConversionServiceHandler(BaseServiceHandler):
    """PDF conversion service handler"""

    def __init__(self, temp_dir: Optional[Path] = None):
        super().__init__()
        self.conversion_operation = ConversionOperation(temp_dir)

    @property
    def service_name(self) -> str:
        """Get service name for registration"""
        return "conversion"

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

        return await self.handle_conversion(
            file=file,
            format=format_type,
            preserve_images=preserve_images,
            preserve_formatting=preserve_formatting
        )

    async def handle_conversion(
        self,
        file: UploadFile,
        format: str,
        preserve_images: bool = True,
        preserve_formatting: bool = True,
    ) -> OperationResult:
        """Handle PDF conversion request"""
        try:
            # Validate format
            try:
                conversion_format = ConversionFormat(format.lower())
            except ValueError:
                raise ValueError(f"Unsupported conversion format: {format}")

            # Save uploaded file
            input_file = await self.save_upload_file_tracked(file)

            # Create conversion options
            options = ConversionOptions(
                format=conversion_format,
                preserve_images=preserve_images,
                preserve_formatting=preserve_formatting,
            )

            # Execute conversion
            result = self.conversion_operation.execute(input_file, options)

            return result

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise