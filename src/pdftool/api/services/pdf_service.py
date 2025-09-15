"""
PDF操作服务层
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException

from ...core.pdf_operations import PDFOperations
from ...core.models import SplitOptions, MergeOptions, ExtractOptions, PageSelectionOptions, SplitMode, PageSelectionMode, OperationResult, PDFInfo
from ...core.exceptions import PDFToolError
from ...config.settings import settings
from ...utils.logging import get_logger
from ..schemas.requests import SplitModeEnum, PageSelectionModeEnum, PDFSplitRequest, PDFMergeRequest, PDFExtractRequest, PDFPageSelectionRequest
from ..schemas.responses import PDFInfoResponse, FileUploadResponse


logger = get_logger("api.pdf_service")


class PDFService:
    """PDF操作业务逻辑服务"""
    
    def __init__(self, pdf_operations: PDFOperations):
        self.pdf_ops = pdf_operations
    
    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        """保存上传的文件到临时目录"""
        try:
            # 验证文件类型
            if not upload_file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="文件必须是PDF格式"
                )
            
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
            raise HTTPException(
                status_code=500,
                detail=f"保存文件失败: {str(e)}"
            )
    
    async def get_upload_file_info(self, upload_file: UploadFile) -> FileUploadResponse:
        """获取上传文件信息"""
        content = await upload_file.read()
        await upload_file.seek(0)  # 重置文件指针
        
        return FileUploadResponse(
            filename=upload_file.filename,
            size=len(content),
            content_type=upload_file.content_type,
            upload_time=datetime.now().isoformat()
        )
    
    async def merge_pdfs(
        self, 
        files: List[UploadFile], 
        request: Optional[PDFMergeRequest] = None
    ) -> OperationResult:
        """合并PDF文件"""
        if len(files) < 2:
            raise HTTPException(
                status_code=400,
                detail="需要至少2个PDF文件"
            )
        
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
    
    async def split_pdf(
        self, 
        file: UploadFile, 
        request: PDFSplitRequest
    ) -> OperationResult:
        """拆分PDF文件"""
        temp_input = None
        try:
            # 保存上传的文件
            temp_input = await self.save_upload_file(file)
            
            # 设置拆分选项
            split_mode = SplitMode.ALL_PAGES if request.mode == SplitModeEnum.ALL else SplitMode.PAGE_RANGE
            options = SplitOptions(
                mode=split_mode,
                start_page=request.start_page,
                end_page=request.end_page,
                filename_prefix=Path(file.filename).stem
            )
            
            # 执行拆分操作
            result = self.pdf_ops.split_pdf(temp_input, options)
            
            if result.success:
                logger.info(f"PDF拆分成功: {file.filename}")
            else:
                logger.error(f"PDF拆分失败: {result.message}")
            
            return result
            
        except PDFToolError as e:
            logger.error(f"PDF拆分失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"PDF拆分异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"拆分PDF时出错: {str(e)}")
        finally:
            # 清理临时文件
            if temp_input:
                self.pdf_ops.cleanup_temp_files([temp_input])
    
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
                file_size=file_size
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
    
    async def extract_pages(
        self, 
        file: UploadFile, 
        request: PDFExtractRequest
    ) -> OperationResult:
        """提取PDF指定页面"""
        temp_input = None
        try:
            # 保存上传的文件
            temp_input = await self.save_upload_file(file)
            
            # 设置提取选项
            options = ExtractOptions(
                pages=request.pages,
                filename_prefix=request.filename_prefix or Path(file.filename).stem
            )
            
            # 执行页面提取操作
            result = self.pdf_ops.extract_pages(temp_input, options)
            
            if result.success:
                logger.info(f"PDF页面提取成功: {file.filename}, 页面: {request.pages}")
            else:
                logger.error(f"PDF页面提取失败: {result.message}")
            
            return result
            
        except PDFToolError as e:
            logger.error(f"PDF页面提取失败: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"PDF页面提取异常: {str(e)}")
            raise HTTPException(status_code=500, detail=f"提取PDF页面时出错: {str(e)}")
        finally:
            # 清理临时文件
            if temp_input:
                self.pdf_ops.cleanup_temp_files([temp_input])
    
    async def select_pages(
        self, 
        file: UploadFile, 
        request: PDFPageSelectionRequest
    ) -> OperationResult:
        """统一的PDF页面选择方法"""
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
                filename_prefix=request.filename_prefix or Path(file.filename).stem
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
                background=BackgroundTask(self.pdf_ops.cleanup_temp_files, cleanup_files)
            )
        else:
            # 单个文件
            return FileResponse(
                output_file,
                media_type="application/pdf",
                filename=f"{filename}.pdf",
                background=BackgroundTask(self.pdf_ops.cleanup_temp_files, [output_file])
            )