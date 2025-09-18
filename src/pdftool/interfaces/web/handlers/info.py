"""
Info service handler
"""

from typing import List

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
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

    async def handle(self, files: List[UploadFile], request: None = None) -> PDFInfoResponse:
        """Handle PDF info request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]
        temp_file = None
        try:
            # Save uploaded file
            temp_file = await self.save_upload_file(file)

            # Get PDF info
            pdf_info = self.info_operation.execute(temp_file)

            # Get file size
            content = await file.read()
            file_size = len(content)

            logger.info(f"获取PDF信息成功: {file.filename}")

            return PDFInfoResponse(
                pages=pdf_info.pages,
                title=pdf_info.title,
                author=pdf_info.author,
                creation_date=str(pdf_info.creation_date) if pdf_info.creation_date else None,
                file_size=file_size,
            )

        except PDFToolError as e:
            logger.error(f"获取PDF信息失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"获取PDF信息异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"读取PDF信息时出错: {str(e)}")
        finally:
            # Cleanup temporary file
            if temp_file and hasattr(self.info_operation, "cleanup_temp_files"):
                self.info_operation.cleanup_temp_files([temp_file])
