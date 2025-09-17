"""
文档域模块

提供文档操作相关的功能，包括：
- PDF合并、拆分、水印、信息提取
- 文档验证
- 操作模型
"""

from .models import (
    DocumentInfoOperation,
    DocumentMergeOperation,
    DocumentOperation,
    DocumentSplitOperation,
    DocumentWatermarkOperation,
)
from .validators import (
    validate_document_files,
    validate_merge_options,
    validate_split_options,
    validate_watermark_options,
)

__all__ = [
    # 模型
    "DocumentOperation",
    "DocumentMergeOperation",
    "DocumentSplitOperation",
    "DocumentWatermarkOperation",
    "DocumentInfoOperation",
    # 验证器
    "validate_document_files",
    "validate_merge_options",
    "validate_split_options",
    "validate_watermark_options",
]
