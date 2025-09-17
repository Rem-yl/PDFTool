"""
文档域数据模型

定义文档操作相关的数据结构。
"""

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from ...common.models import MergeOptions, SplitOptions, WatermarkOptions


class DocumentOperation(BaseModel):
    """文档操作基础模型"""

    operation_type: str
    input_files: List[Path]
    output_path: Optional[Path] = None
    temp_dir: Optional[Path] = None


class DocumentMergeOperation(DocumentOperation):
    """文档合并操作模型"""

    operation_type: str = "merge"
    options: MergeOptions


class DocumentSplitOperation(DocumentOperation):
    """文档拆分操作模型"""

    operation_type: str = "split"
    options: SplitOptions


class DocumentWatermarkOperation(DocumentOperation):
    """文档水印操作模型"""

    operation_type: str = "watermark"
    options: WatermarkOptions


class DocumentInfoOperation(DocumentOperation):
    """文档信息提取操作模型"""

    operation_type: str = "info"
