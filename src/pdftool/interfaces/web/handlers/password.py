"""
Password protection service handler
"""

from typing import List

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
from ....common.models import OperationResult, PasswordProtectionOptions
from ....common.utils.logging import get_logger
from ....domains.document.operations import PasswordProtectionOperation
from ..interfaces import BaseServiceHandler
from ..schemas.requests import PasswordProtectionRequest

logger = get_logger("api.handlers.password")


class PasswordProtectionServiceHandler(BaseServiceHandler):
    """Service handler for PDF password protection operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_operation = PasswordProtectionOperation()

    @property
    def service_name(self) -> str:
        return "password"

    async def handle(
        self, files: List[UploadFile], request: PasswordProtectionRequest, *args, **kwargs
    ) -> OperationResult:
        """Handle PDF password protection request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]
        try:
            # Save uploaded file using tracked method
            temp_input = await self.save_upload_file_tracked(file)

            # Create password protection options
            options = PasswordProtectionOptions(
                user_password=request.user_password,
                owner_password=request.owner_password,
                allow_printing=request.allow_printing,
                allow_copying=request.allow_copying,
                allow_modification=request.allow_modification,
                allow_annotation=request.allow_annotation,
                allow_filling_forms=request.allow_filling_forms,
                allow_screen_readers=request.allow_screen_readers,
                allow_assembly=request.allow_assembly,
                allow_degraded_printing=request.allow_degraded_printing,
            )

            # Execute password protection operation
            result = self.password_operation.execute(temp_input, options)

            logger.info(f"密码保护操作成功: {file.filename}")
            return result

        except PDFToolError as e:
            logger.error(f"密码保护失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"密码保护异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"密码保护时出错: {str(e)}")
