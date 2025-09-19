"""
API service interfaces
"""

import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List

from fastapi import HTTPException, UploadFile

from ...common.models import OperationResult
from ...common.utils.logging import get_logger

logger = get_logger("api.interfaces")


class IServiceHandler(ABC):
    """Base interface for API service handlers"""

    @abstractmethod
    async def handle(
        self, files: List[UploadFile], request: Any, *args, **kwargs
    ) -> OperationResult:
        """Handle the service request"""

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Get service name for registration"""


class IServiceRegistry(ABC):
    """Interface for service registry"""

    @abstractmethod
    def register_handler(self, service_name: str, handler_class: type) -> None:
        """Register a service handler"""

    @abstractmethod
    def get_handler(self, service_name: str) -> IServiceHandler:
        """Get a service handler by name"""

    @abstractmethod
    def list_services(self) -> list[str]:
        """List all registered services"""


class BaseServiceHandler(IServiceHandler):
    """
    解耦的服务处理器基类
    使用依赖注入获取所需的服务
    """

    def __init__(self, *args, **kwargs):
        # 存储当前请求的所有临时文件，用于统一清理
        self._temp_files_registry = []

    async def save_upload_file(self, upload_file: UploadFile, validate_pdf: bool = True) -> Path:
        """Save uploaded file to temporary directory"""
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        try:
            # Validate file type if requested
            if validate_pdf and not upload_file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="文件必须是PDF格式")

            # Create temporary file
            suffix = Path(upload_file.filename).suffix if upload_file.filename else ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await upload_file.read()
                tmp.write(content)
                temp_path = Path(tmp.name)

            logger.info(f"保存上传文件: {upload_file.filename} -> {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"保存上传文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

    async def save_upload_file_tracked(
        self, upload_file: UploadFile, validate_pdf: bool = True
    ) -> Path:
        """保存上传文件并跟踪以便统一清理"""
        temp_path = await self.save_upload_file(upload_file, validate_pdf)
        # 将临时文件添加到注册表中，但不立即清理
        if not hasattr(self, "_temp_files_registry"):
            self._temp_files_registry = []
        self._temp_files_registry.append(temp_path)
        return temp_path

    def _cleanup_files(self, files: list):
        """Simple cleanup function for temporary files"""
        import os

        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.info(f"已清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理文件失败 {file_path}: {str(e)}")

    def create_archive(self, file_paths, output_zip="output.zip"):
        """
        将多个文件打包成一个 zip 压缩包

        Args:
            file_paths (list[str]): 要打包的文件路径列表
            output_zip (str): 输出的 zip 文件路径
        """
        import os
        import zipfile

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in file_paths:
                arcname = os.path.basename(file)  # 只保留文件名，不带路径
                zipf.write(file, arcname)

        return output_zip

    def create_download_response(self, result: OperationResult, filename: str):
        """Create file download response with comprehensive cleanup"""
        from fastapi.responses import FileResponse
        from starlette.background import BackgroundTask

        if not result.success or not result.output_files:
            raise HTTPException(status_code=500, detail="没有可下载的文件")

        output_file = result.output_files[0]

        # 收集所有需要清理的文件：输入文件 + 输出文件
        all_cleanup_files = []

        # 添加跟踪的临时输入文件
        if hasattr(self, "_temp_files_registry"):
            all_cleanup_files.extend(self._temp_files_registry)

        # Choose download type based on number of files
        if len(result.output_files) > 1:
            zip_file = self.create_archive(result.output_files)
            # 添加输出文件和ZIP文件到清理列表
            all_cleanup_files.extend(result.output_files)
            all_cleanup_files.append(zip_file)

            return FileResponse(
                path=str(zip_file),
                filename=f"{filename}.zip",
                media_type="application/zip",
                background=BackgroundTask(self._cleanup_files, all_cleanup_files),
            )

        # 添加输出文件到清理列表
        all_cleanup_files.extend(result.output_files)

        return FileResponse(
            path=str(output_file),
            filename=f"{filename}.pdf",
            media_type="application/pdf",
            background=BackgroundTask(self._cleanup_files, all_cleanup_files),
        )
