"""
公共组件模块

提供系统级的共享组件，包括：
- 核心接口定义
- 数据模型
- 异常类型
- 工具函数
"""

from .exceptions import (
    PDFFileNotFoundError,
    PDFProcessingError,
    PDFToolError,
    PDFValidationError,
)
from .interfaces import BasePDFOperation
from .models import (
    MergeOptions,
    OperationResult,
    PDFInfo,
    SplitMode,
    SplitOptions,
    WatermarkOptions,
)

__all__ = [
    # 核心接口
    "BasePDFOperation",
    # 模型
    "PDFInfo",
    "SplitOptions",
    "MergeOptions",
    "WatermarkOptions",
    "OperationResult",
    "SplitMode",
    # 异常
    "PDFToolError",
    "PDFValidationError",
    "PDFProcessingError",
    "PDFFileNotFoundError",
]
