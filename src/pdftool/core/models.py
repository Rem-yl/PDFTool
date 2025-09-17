"""
Data models and types for PDFTool operations
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class PageSelectionMode(Enum):
    """PDF页面选择模式"""

    ALL_PAGES = "all"  # 全部页面（每页单独文件）
    SPECIFIC_PAGES = "pages"  # 指定页面列表（每页单独文件）
    SINGLE_FILE = "single"  # 将选中页面合并为单个文件


# 保持向后兼容
SplitMode = PageSelectionMode


@dataclass
class PDFInfo:
    """PDF metadata information"""

    pages: int
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    file_size: Optional[int] = None
    file_path: Optional[Path] = None


@dataclass
class PageSelectionOptions:
    """统一的PDF页面选择操作选项"""

    mode: PageSelectionMode
    # 页面选择参数
    pages: Optional[List[int]] = None  # 指定页面列表（SPECIFIC_PAGES/SINGLE_FILE模式）
    # 输出参数
    output_dir: Optional[Path] = None
    filename_prefix: Optional[str] = None
    output_format: str = "pdf"


# 保持向后兼容的别名
@dataclass
class SplitOptions:
    """Options for PDF splitting operations"""

    mode: PageSelectionMode
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    output_dir: Optional[Path] = None
    filename_prefix: Optional[str] = None


@dataclass
class ExtractOptions:
    """Options for PDF page extraction operations"""

    pages: List[int]
    output_dir: Optional[Path] = None
    filename_prefix: Optional[str] = None
    output_format: str = "pdf"


@dataclass
class MergeOptions:
    """Options for PDF merging operations"""

    output_file: Optional[Path] = None
    preserve_bookmarks: bool = True
    preserve_metadata: bool = True


@dataclass
class OperationResult:
    """Result of a PDF operation"""

    success: bool
    message: str
    output_files: List[Path]
    details: Optional[str] = None
