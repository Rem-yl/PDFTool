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
    async def handle(self, files: List[UploadFile], request_data: Any) -> OperationResult:
        """Handle the service request"""
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Get service name for registration"""
        pass


class IServiceRegistry(ABC):
    """Interface for service registry"""

    @abstractmethod
    def register_handler(self, service_name: str, handler_class: type) -> None:
        """Register a service handler"""
        pass

    @abstractmethod
    def get_handler(self, service_name: str) -> IServiceHandler:
        """Get a service handler by name"""
        pass

    @abstractmethod
    def list_services(self) -> list[str]:
        """List all registered services"""
        pass


class BaseServiceHandler(IServiceHandler):
    """
    解耦的服务处理器基类
    使用依赖注入获取所需的服务
    """

    def __init__(self, operation_executor=None, resource_manager=None):
        """
        初始化服务处理器

        Args:
            operation_executor: 操作执行器
            resource_manager: 资源管理器
        """
        self.operation_executor = operation_executor
        self.resource_manager = resource_manager

    async def save_upload_file(self, upload_file: UploadFile, validate_pdf: bool = True) -> Path:
        """Save uploaded file to temporary directory"""
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

    def create_download_response(self, result: OperationResult, filename: str):
        """Create file download response"""
        from fastapi.responses import FileResponse
        from starlette.background import BackgroundTask

        if not result.success or not result.output_files:
            raise HTTPException(status_code=500, detail="没有可下载的文件")

        output_file = result.output_files[0]

        # Choose download type based on number of files
        if len(result.output_files) > 1:
            # Multiple files, create ZIP archive
            if self.resource_manager is None:
                raise HTTPException(status_code=500, detail="资源管理器未初始化，无法处理多文件")

            zip_file = self.resource_manager.create_archive(result.output_files)
            cleanup_files = [zip_file] + result.output_files
            return FileResponse(
                path=str(zip_file),
                filename=f"{filename}.zip",
                media_type="application/zip",
                background=BackgroundTask(self.resource_manager.cleanup_resources, cleanup_files),
            )
        else:
            # Single file - use simple cleanup if no resource manager
            cleanup_func = (
                self.resource_manager.cleanup_resources
                if self.resource_manager
                else self._cleanup_files
            )
            return FileResponse(
                path=str(output_file),
                filename=f"{filename}.pdf",
                media_type="application/pdf",
                background=BackgroundTask(cleanup_func, [output_file]),
            )
