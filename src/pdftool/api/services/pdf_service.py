"""
PDF操作服务层
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, UploadFile

from ...core.exceptions import PDFToolError
from ...core.models import (
    MergeOptions,
    OperationResult,
    PageSelectionMode,
    PageSelectionOptions,
    WatermarkOptions,
    WatermarkPosition,
    WatermarkType,
)
from ...core.pdf_operations import PDFOperations
from ...utils.logging import get_logger
from ..schemas.requests import (
    PageSelectionModeEnum,
    PDFMergeRequest,
    PDFPageSelectionRequest,
    WatermarkRequest,
)
from ..schemas.responses import FileUploadResponse, PDFInfoResponse

logger = get_logger("api.pdf_service")


class PDFService:
    """PDF操作业务逻辑服务"""

    def __init__(self, pdf_operations: PDFOperations):
        self.pdf_ops = pdf_operations

    async def save_upload_file(self, upload_file: UploadFile, validate_pdf: bool = True) -> Path:
        """保存上传的文件到临时目录"""
        try:
            # 验证文件类型
            if validate_pdf and not upload_file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="文件必须是PDF格式")

            # 创建临时文件
            suffix = Path(upload_file.filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await upload_file.read()
                tmp.write(content)
                temp_path = Path(tmp.name)

            logger.info(f"保存上传文件: {upload_file.filename} -> {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"保存上传文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

    async def get_upload_file_info(self, upload_file: UploadFile) -> FileUploadResponse:
        """获取上传文件信息"""
        content = await upload_file.read()
        await upload_file.seek(0)  # 重置文件指针

        return FileUploadResponse(
            filename=upload_file.filename,
            size=len(content),
            content_type=upload_file.content_type,
            upload_time=datetime.now().isoformat(),
        )

    async def merge_pdfs(
        self, files: List[UploadFile], request: Optional[PDFMergeRequest] = None
    ) -> OperationResult:
        """合并PDF文件"""
        if len(files) < 2:
            raise HTTPException(status_code=400, detail="需要至少2个PDF文件")

        temp_files = []
        try:
            # 保存所有上传的文件
            for file in files:
                temp_path = await self.save_upload_file(file)
                temp_files.append(temp_path)

            # 设置合并选项
            options = MergeOptions()
            if request:
                options.preserve_bookmarks = request.preserve_bookmarks
                options.preserve_metadata = request.preserve_metadata

            # 执行合并操作
            result = self.pdf_ops.merge_pdfs(temp_files, options)

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
            # 清理临时文件
            self.pdf_ops.cleanup_temp_files(temp_files)

    async def get_pdf_info(self, file: UploadFile) -> PDFInfoResponse:
        """获取PDF文件信息"""
        temp_file = None
        try:
            # 保存上传的文件
            temp_file = await self.save_upload_file(file)

            # 获取PDF信息
            pdf_info = self.pdf_ops.get_pdf_info(temp_file)

            # 获取文件大小
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
            # 清理临时文件
            if temp_file:
                self.pdf_ops.cleanup_temp_files([temp_file])

    async def select_pages(
        self, file: UploadFile, request: PDFPageSelectionRequest
    ) -> OperationResult:
        """统一的PDF页面选择方法"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件不能为空")

        temp_input = None
        try:
            # 保存上传的文件
            temp_input = await self.save_upload_file(file)

            # 转换请求模式
            if request.mode == PageSelectionModeEnum.ALL:
                mode = PageSelectionMode.ALL_PAGES
            elif request.mode == PageSelectionModeEnum.PAGES:
                mode = PageSelectionMode.SPECIFIC_PAGES
            elif request.mode == PageSelectionModeEnum.SINGLE:
                mode = PageSelectionMode.SINGLE_FILE
            else:
                raise HTTPException(status_code=400, detail=f"不支持的模式: {request.mode}")

            # 设置页面选择选项
            options = PageSelectionOptions(
                mode=mode,
                pages=request.pages,
                filename_prefix=request.filename_prefix or Path(file.filename).stem,
            )

            # 执行页面选择操作
            result = self.pdf_ops.select_pages(temp_input, options)

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
            # 清理临时文件
            if temp_input:
                self.pdf_ops.cleanup_temp_files([temp_input])

    async def add_watermark(
        self, file: UploadFile, watermark_file: Optional[UploadFile], request: WatermarkRequest
    ) -> OperationResult:
        """添加水印到PDF"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件不能为空")

        temp_input = None
        temp_watermark_image = None
        try:
            # 保存上传的PDF文件
            temp_input = await self.save_upload_file(file)

            # 处理水印图片（如果是图片水印）
            if request.watermark_type.value == "image" and watermark_file:
                temp_watermark_image = await self.save_upload_file(
                    watermark_file, validate_pdf=False
                )

            # 解析页面列表
            specific_pages = None
            if request.page_selection in ["pages", "range"] and request.specific_pages:
                try:
                    from ..dependencies import parse_page_list

                    specific_pages = parse_page_list(request.specific_pages)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"页面格式错误: {str(e)}")

            # 转换枚举值
            watermark_type = (
                WatermarkType.TEXT
                if request.watermark_type.value == "text"
                else WatermarkType.IMAGE
            )
            position = WatermarkPosition(request.position.value)

            # 页面选择模式转换
            if request.page_selection == "all":
                page_selection = PageSelectionMode.ALL_PAGES
            else:
                page_selection = PageSelectionMode.SPECIFIC_PAGES

            # 创建水印选项
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

            # 执行水印操作
            result = self.pdf_ops.add_watermark(temp_input, options)

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
        finally:
            # 清理临时文件
            temp_files = []
            if temp_input:
                temp_files.append(temp_input)
            if temp_watermark_image:
                temp_files.append(temp_watermark_image)
            if temp_files:
                self.pdf_ops.cleanup_temp_files(temp_files)

    def create_download_response(self, result: OperationResult, filename: str):
        """创建文件下载响应"""
        from fastapi.responses import FileResponse
        from starlette.background import BackgroundTask

        if not result.success or not result.output_files:
            raise HTTPException(status_code=500, detail="没有可下载的文件")

        output_file = result.output_files[0]

        # 根据文件数量决定下载类型
        if len(result.output_files) > 1:
            # 多个文件，创建ZIP包
            zip_file = self.pdf_ops.create_zip_archive(result.output_files)
            cleanup_files = [zip_file] + result.output_files
            return FileResponse(
                zip_file,
                media_type="application/zip",
                filename=f"{filename}.zip",
                background=BackgroundTask(self.pdf_ops.cleanup_temp_files, cleanup_files),
            )
        else:
            # 单个文件
            return FileResponse(
                output_file,
                media_type="application/pdf",
                filename=f"{filename}.pdf",
                background=BackgroundTask(self.pdf_ops.cleanup_temp_files, [output_file]),
            )
