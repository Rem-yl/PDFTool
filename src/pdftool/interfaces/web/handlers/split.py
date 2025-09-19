"""
Split service handler
"""

from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
from ....common.models import OperationResult, PageSelectionMode, PageSelectionOptions
from ....common.utils.logging import get_logger
from ....domains.document.operations import SplitOperation
from ..interfaces import BaseServiceHandler
from ..schemas.requests import PageSelectionModeEnum, PDFPageSelectionRequest

logger = get_logger("api.handlers.split")


class SplitServiceHandler(BaseServiceHandler):
    """Service handler for PDF split operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.split_operation = SplitOperation()

    @property
    def service_name(self) -> str:
        return "split"

    async def handle(
        self, files: List[UploadFile], request: PDFPageSelectionRequest, *args, **kwargs
    ) -> OperationResult:
        """Handle PDF split request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]
        try:
            # Save uploaded file using tracked method
            temp_input = await self.save_upload_file_tracked(file)

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
                filename_prefix=request.filename_prefix or Path(file.filename or "document").stem,
            )

            # Execute split operation
            result = self.split_operation.execute(temp_input, options)

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
        # 注意：不再有 finally 清理，所有文件将在下载完成后统一清理
