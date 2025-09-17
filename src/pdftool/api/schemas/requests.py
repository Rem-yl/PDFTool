"""
API请求模型定义
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PageSelectionModeEnum(str, Enum):
    """PDF页面选择模式枚举"""

    ALL = "all"  # 全部页面（每页单独文件）
    PAGES = "pages"  # 指定页面列表（每页单独文件）
    SINGLE = "single"  # 将选中页面合并为单个文件
    RANGE = "range"  #  指定页面范围


class WatermarkTypeEnum(str, Enum):
    """水印类型枚举"""

    TEXT = "text"  # 文本水印
    IMAGE = "image"  # 图片水印


class WatermarkPositionEnum(int, Enum):
    """水印位置枚举"""

    TOP_LEFT = 1  # 左上角
    TOP_CENTER = 2  # 右上角
    TOP_RIGHT = 3  # 左下角
    CENTER_LEFT = 4  # 右下角
    CENTER = 5
    CENTER_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_CENTER = 8
    BOTTOM_RIGHT = 9


class WatermarkPageSelectionModeEnum(str, Enum):
    """PDF页面选择模式枚举"""

    ALL = "all"  # 全部页面（每页单独文件）
    PAGES = "pages"  # 指定页面列表（每页单独文件）
    SPECIFIC = "specific"  # 将选中页面合并为单个文件


class PDFMergeRequest(BaseModel):
    """PDF合并请求模型"""

    preserve_bookmarks: bool = Field(True, description="是否保留书签")
    preserve_metadata: bool = Field(True, description="是否保留元数据")


class PDFPageSelectionRequest(BaseModel):
    """统一的PDF页面选择请求模型"""

    mode: PageSelectionModeEnum = Field(..., description="页面选择模式")
    # 页面选择参数
    pages: Optional[List[int]] = Field(None, description="指定页面列表（pages/single模式使用）")
    # 输出选项
    filename_prefix: Optional[str] = Field(None, description="输出文件名前缀")

    @validator("pages")
    def validate_pages(cls, v, values):
        mode = values.get("mode")
        if mode in [PageSelectionModeEnum.PAGES, PageSelectionModeEnum.SINGLE]:
            if not v:
                raise ValueError("pages和single模式需要指定页面列表")
            if any(page < 1 for page in v):
                raise ValueError("页面号必须从1开始")
            if len(set(v)) != len(v):
                raise ValueError("页面号不能重复")
            return sorted(v)
        return v


# 保持向后兼容的别名
class PDFExtractRequest(BaseModel):
    """PDF页面提取请求模型"""

    pages: List[int] = Field(..., description="要提取的页面列表，从1开始")
    filename_prefix: Optional[str] = Field(None, description="输出文件名前缀")

    @validator("pages")
    def validate_pages(cls, v):
        if not v:
            raise ValueError("至少需要指定一个页面")
        if any(page < 1 for page in v):
            raise ValueError("页面号必须从1开始")
        if len(set(v)) != len(v):
            raise ValueError("页面号不能重复")
        return sorted(v)


class UploadConfig(BaseModel):
    """上传配置模型"""

    max_file_size: int = Field(100 * 1024 * 1024, description="最大文件大小")
    allowed_extensions: list = Field([".pdf"], description="允许的文件扩展名")
