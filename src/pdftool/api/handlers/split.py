"""
Split service handler
"""

from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile

from ...core.exceptions import PDFToolError
from ...core.models import OperationResult, PageSelectionMode, PageSelectionOptions
from ...utils.logging import get_logger
from ..interfaces import BaseServiceHandler
from ..schemas.requests import PageSelectionModeEnum, PDFPageSelectionRequest

logger = get_logger("api.handlers.split")


class SplitServiceHandler(BaseServiceHandler):
    """Service handler for PDF split operations"""

    @property
    def service_name(self) -> str:
        return "split"

    async def handle(
        self, files: List[UploadFile], request: PDFPageSelectionRequest
    ) -> OperationResult:
        """Handle PDF split request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]
        temp_input = None
        try:
            # Save uploaded file
            temp_input = await self.save_upload_file(file)

            # Convert request mode
            if request.mode == PageSelectionModeEnum.ALL:
                mode = PageSelectionMode.ALL_PAGES
            elif request.mode == PageSelectionModeEnum.PAGES:
                mode = PageSelectionMode.SPECIFIC_PAGES
            elif request.mode == PageSelectionModeEnum.SINGLE:
                mode = PageSelectionMode.SINGLE_FILE
            else:
                raise HTTPException(status_code=400, detail=f"不支持的模式: {request.mode}")

            # Set page selection options
            options = PageSelectionOptions(
                mode=mode,
                pages=request.pages,
                filename_prefix=request.filename_prefix or Path(file.filename).stem,
            )

            # Execute split operation
            result = self.pdf_processor.split_pdf(temp_input, options)

            if result.success:
                logger.info(f"PDF页面选择成功: {file.filename}, 模式: {request.mode}")
            else:
                logger.error(f"PDF页面选择失败: {result.message}")

            return result

        except PDFToolError as e:
            logger.error(f"PDF页面选择失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"PDF页面选择异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"页面选择时出错: {str(e)}")
        finally:
            # Cleanup temporary file
            if temp_input and self.pdf_processor:
                self.pdf_processor.cleanup_temp_files([temp_input])
