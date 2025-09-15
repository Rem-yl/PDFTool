"""
FastAPI依赖注入
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from pathlib import Path

from ..core.pdf_operations import PDFOperations
from ..config.settings import settings
from ..utils.logging import get_logger


logger = get_logger("api.dependencies")


def get_pdf_operations() -> PDFOperations:
    """获取PDF操作实例"""
    return PDFOperations(temp_dir=settings.temp_dir)


def get_settings():
    """获取应用设置"""
    return settings


def validate_file_size(file_size: int) -> bool:
    """验证文件大小"""
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 {settings.max_file_size / 1024 / 1024:.1f}MB"
        )
    return True


def validate_file_extension(filename: str) -> bool:
    """验证文件扩展名"""
    file_path = Path(filename)
    if file_path.suffix.lower() not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(settings.allowed_extensions)}"
        )
    return True


class CommonQueryParams:
    """通用查询参数"""
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        debug: bool = False
    ):
        self.skip = skip
        self.limit = limit
        self.debug = debug