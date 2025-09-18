"""
Merge service handler
"""

from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
from ....common.models import MergeOptions, OperationResult
from ....common.utils.logging import get_logger
from ....domains.document.operations import MergeOperation
from ..interfaces import BaseServiceHandler
from ..schemas.requests import PDFMergeRequest

logger = get_logger("api.handlers.merge")


class MergeServiceHandler(BaseServiceHandler):
    """Service handler for PDF merge operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.merge_operation = MergeOperation()

    @property
    def service_name(self) -> str:
        return "merge"

    async def handle(self, files: List[UploadFile], request: PDFMergeRequest) -> OperationResult:
        """Handle PDF merge request"""
        if len(files) < 2:
            raise HTTPException(status_code=400, detail="需要至少2个PDF文件")

        temp_files = []
        try:
            # Save all uploaded files
            for file in files:
                temp_path = await self.save_upload_file(file)
                temp_files.append(temp_path)

            # Set merge options
            options = MergeOptions()
            if request:
                options.preserve_bookmarks = request.preserve_bookmarks
                options.preserve_metadata = request.preserve_metadata

            # Execute merge operation
            result = self.merge_operation.execute(temp_files, options)

            if result.success:
                logger.info(f"PDF合并成功: {len(files)}个文件")
            else:
                logger.error(f"PDF合并失败: {result.message}")

            return result

        except PDFToolError as e:
            logger.error(f"PDF合并失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"PDF合并异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"合并PDF时出错: {str(e)}")
        finally:
            # Cleanup temporary files
            if hasattr(self.merge_operation, "cleanup_temp_files"):
                self.merge_operation.cleanup_temp_files(temp_files)
