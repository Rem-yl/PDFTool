"""
Merge service handler
"""

from typing import List

from fastapi import HTTPException, UploadFile

from ....common.models import MergeOptions, OperationResult
from ....common.utils.logging import get_logger
from ....domains.document.operations.merge import MergeOperation
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
        for file in files:
            temp_path = await self.save_upload_file_tracked(file)
            temp_files.append(temp_path)

        options = MergeOptions()
        if request:
            options.preserve_bookmarks = request.preserve_bookmarks
            options.preserve_metadata = request.preserve_metadata

        # Execute merge operation
        result = self.merge_operation.execute(temp_files, options)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        logger.info(f"PDF合并成功: {len(files)}个文件")

        return result
