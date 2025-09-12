"""
Data models and types for PDFTool operations
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class SplitMode(Enum):
    """PDF splitting modes"""
    ALL_PAGES = "all"
    PAGE_RANGE = "range"


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
class SplitOptions:
    """Options for PDF splitting operations"""
    mode: SplitMode
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    output_dir: Optional[Path] = None
    filename_prefix: Optional[str] = None


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