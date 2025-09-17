"""
FastAPI依赖注入
"""

from pathlib import Path
from typing import Generator

from fastapi import Depends, HTTPException, status

from ..config.settings import settings
from ..core.pdf_operations import PDFOperations
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
            detail=f"文件大小超过限制 {settings.max_file_size / 1024 / 1024:.1f}MB",
        )
    return True


def validate_file_extension(filename: str | None) -> bool:
    """验证文件扩展名"""
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    file_path = Path(filename)
    if file_path.suffix.lower() not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(settings.allowed_extensions)}",
        )
    return True


def parse_page_list(pages: str) -> list[int]:
    page_list = []
    for part in pages.split(","):
        part = part.strip()
        if "-" in part:
            # 处理范围格式 "1-5"
            start, end = map(int, part.split("-"))
            if start > end:
                raise HTTPException(
                    status_code=400, detail=f"页面范围错误: {start}-{end}，起始页不能大于结束页"
                )
            page_list.extend(range(start, end + 1))
        else:
            # 处理单个页面
            page_list.append(int(part))
    page_list = sorted(list(set(page_list)))  # 去重并排序

    return page_list


class CommonQueryParams:
    """通用查询参数"""

    def __init__(self, skip: int = 0, limit: int = 100, debug: bool = False):
        self.skip = skip
        self.limit = limit
        self.debug = debug
