"""
Watermark service handler
"""

from typing import List, Optional

from fastapi import HTTPException, UploadFile

from ....common.exceptions import PDFToolError
from ....common.models import (
    OperationResult,
    PageSelectionMode,
    WatermarkOptions,
    WatermarkPosition,
    WatermarkType,
)
from ....common.utils.logging import get_logger
from ....domains.document.operations import WatermarkOperation
from ..interfaces import BaseServiceHandler
from ..schemas.requests import WatermarkRequest

logger = get_logger("api.handlers.watermark")


class WatermarkServiceHandler(BaseServiceHandler):
    """Service handler for PDF watermark operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watermark_operation = WatermarkOperation()

    @property
    def service_name(self) -> str:
        return "watermark"

    async def handle(
        self,
        files: List[UploadFile],
        request: WatermarkRequest,
        watermark_file: Optional[UploadFile] = None,
    ) -> OperationResult:
        """Handle PDF watermark request"""
        if len(files) != 1:
            raise HTTPException(status_code=400, detail="只能处理一个PDF文件")

        file = files[0]

        try:
            # 保存输入文件，使用跟踪机制
            temp_input = await self.save_upload_file_tracked(file)

            # 保存水印图片文件（如果需要）
            temp_watermark_image = None
            if request.watermark_type.value == "image" and watermark_file:
                temp_watermark_image = await self.save_upload_file_tracked(
                    watermark_file, validate_pdf=False
                )

            # Parse page list
            specific_pages = None
            if request.page_selection in ["pages", "range"] and request.specific_pages:
                try:
                    from ..dependencies import parse_page_list

                    specific_pages = parse_page_list(request.specific_pages)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"页面格式错误: {str(e)}")

            # Convert enum values
            watermark_type = (
                WatermarkType.TEXT
                if request.watermark_type.value == "text"
                else WatermarkType.IMAGE
            )
            position = WatermarkPosition(request.position.value)

            # Page selection mode conversion
            if request.page_selection == "all":
                page_selection = PageSelectionMode.ALL_PAGES
            else:
                page_selection = PageSelectionMode.SPECIFIC_PAGES

            # Create watermark options
            options = WatermarkOptions(
                watermark_type=watermark_type,
                position=position,
                opacity=request.opacity,
                text=request.watermark_text,
                font_size=request.font_size,
                font_color=request.font_color,
                image_path=temp_watermark_image,
                image_scale=request.image_scale,
                page_selection=page_selection,
                specific_pages=specific_pages,
            )

            # Execute watermark operation
            result = self.watermark_operation.execute(temp_input, options)

            if result.success:
                logger.info(f"PDF水印添加成功: {file.filename}")
            else:
                logger.error(f"PDF水印添加失败: {result.message}")

            return result

        except PDFToolError as e:
            logger.error(f"PDF水印添加失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"PDF水印添加异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"添加水印时出错: {str(e)}")
