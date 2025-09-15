"""
API请求模型定义
"""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class SplitModeEnum(str, Enum):
    """PDF拆分模式枚举"""
    ALL = "all"
    RANGE = "range"


class PDFSplitRequest(BaseModel):
    """PDF拆分请求模型"""
    mode: SplitModeEnum
    start_page: Optional[int] = Field(None, ge=1, description="起始页码")
    end_page: Optional[int] = Field(None, ge=1, description="结束页码")


class PDFMergeRequest(BaseModel):
    """PDF合并请求模型"""
    preserve_bookmarks: bool = Field(True, description="是否保留书签")
    preserve_metadata: bool = Field(True, description="是否保留元数据")


class UploadConfig(BaseModel):
    """上传配置模型"""
    max_file_size: int = Field(100 * 1024 * 1024, description="最大文件大小")
    allowed_extensions: list = Field([".pdf"], description="允许的文件扩展名")