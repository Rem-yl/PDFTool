"""
API请求模型定义
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class PageSelectionModeEnum(str, Enum):
    """PDF页面选择模式枚举"""

    ALL = "all"  # 全部页面（每页单独文件）
    PAGES = "pages"  # 指定页面列表（每页单独文件）
    SINGLE = "single"  # 将选中页面合并为单个文件
    RANGE = "range"  # 指定页面范围


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
    def validate_pages(cls, v: Optional[List[int]], values: Dict[str, Any]) -> Optional[List[int]]:
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
    def validate_pages(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("至少需要指定一个页面")
        if any(page < 1 for page in v):
            raise ValueError("页面号必须从1开始")
        if len(set(v)) != len(v):
            raise ValueError("页面号不能重复")
        return sorted(v)


class WatermarkRequest(BaseModel):
    """水印请求模型"""

    watermark_type: WatermarkTypeEnum = Field(..., description="水印类型")
    position: WatermarkPositionEnum = Field(..., description="水印位置")
    opacity: float = Field(..., ge=0.1, le=1.0, description="透明度(0.1-1.0)")

    # 文本水印参数
    watermark_text: Optional[str] = Field(None, description="水印文本")
    font_size: Optional[int] = Field(36, ge=12, le=100, description="字体大小")
    font_color: Optional[str] = Field("#000000", description="字体颜色(十六进制)")

    # 图片水印参数
    image_scale: Optional[float] = Field(100, ge=10, le=300, description="图片缩放百分比")

    # 页面选择
    page_selection: PageSelectionModeEnum = Field(
        PageSelectionModeEnum.ALL, description="页面选择模式"
    )
    specific_pages: Optional[str] = Field(None, description="指定页面(如: 1,3,5-8)")

    @validator("watermark_text")
    def validate_text_watermark(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.get("watermark_type") == WatermarkTypeEnum.TEXT and not v:
            raise ValueError("文本水印需要提供水印文本")
        return v

    @validator("font_color")
    def validate_font_color(cls, v: Optional[str]) -> Optional[str]:
        if v and (not v.startswith("#") or len(v) != 7):
            raise ValueError("字体颜色必须是7位十六进制格式 (#RRGGBB)")
        return v


class UploadConfig(BaseModel):
    """上传配置模型"""

    max_file_size: int = Field(100 * 1024 * 1024, description="最大文件大小")
    allowed_extensions: list = Field([".pdf"], description="允许的文件扩展名")
