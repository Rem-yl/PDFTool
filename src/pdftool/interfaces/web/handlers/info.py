"""
Info service handler
"""

from typing import List

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
from ....common.models import OperationResult
from ....common.utils.logging import get_logger
from ....domains.document.operations import InfoOperation
from ..interfaces import BaseServiceHandler
from ..schemas.responses import PDFInfoResponse

logger = get_logger("api.handlers.info")


class InfoServiceHandler(BaseServiceHandler):
    """Service handler for PDF info operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info_operation = InfoOperation()

    @property
    def service_name(self) -> str:
        return "info"

    async def handle(self, files: List[UploadFile]) -> OperationResult:
        """Handle PDF info request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]
        try:
            # Save uploaded file using tracked method
            temp_file = await self.save_upload_file_tracked(file)

            # Get PDF info
            pdf_info = self.info_operation.execute(temp_file)

            # Get file size
            content = await file.read()
            file_size = len(content)

            logger.info(f"获取PDF信息成功: {file.filename}")

            # 创建 PDFInfoResponse 对象
            pdf_response = PDFInfoResponse(
                pages=pdf_info.pages,
                title=pdf_info.title,
                author=pdf_info.author,
                creation_date=str(pdf_info.creation_date) if pdf_info.creation_date else None,
                file_size=file_size,
            )

            # 返回 OperationResult，将响应数据放在 details 中
            import json

            return OperationResult(
                success=True,
                message="PDF信息获取成功",
                output_files=[],  # info 操作不产生输出文件
                details=json.dumps(pdf_response.model_dump()),  # 将响应数据存储在 details 中
            )

        except PDFToolError as e:
            logger.error(f"获取PDF信息失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"获取PDF信息异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"读取PDF信息时出错: {str(e)}")
