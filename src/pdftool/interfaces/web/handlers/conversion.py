"""
Enhanced conversion service handler with OCR support
"""

import logging
from typing import List

from fastapi import HTTPException, UploadFile

from ....common.models import ConversionOptions, OperationResult
from ....domains.document.operations.conversion import ConversionOperation
from ..interfaces import BaseServiceHandler
from ..schemas.requests import ConversionRequest

logger = logging.getLogger(__name__)


class ConversionServiceHandler(BaseServiceHandler):
    """Enhanced service handler for PDF conversion with OCR support"""

    @property
    def service_name(self) -> str:
        return "conversion"

    def __init__(self):
        super().__init__()
        self.operation = ConversionOperation()

    async def handle(
        self, files: List[UploadFile], request: ConversionRequest, *args, **kwargs
    ) -> OperationResult:
        """Handle conversion request via standard interface"""
        if not files:
            raise ValueError("No files provided for conversion")

        file = files[0]  # Take first file
        temp_input = await self.save_upload_file_tracked(file)
        options = ConversionOptions(
            format=request.format,
        )

        result = self.operation.execute(temp_input, options)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        logger.info(f"格式转换成功: {file.filename}")

        return result
