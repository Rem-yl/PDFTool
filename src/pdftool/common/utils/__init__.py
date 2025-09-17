"""
公共工具模块

提供系统级的工具函数，包括：
- 日志配置
- 数据验证
- 文件操作
"""

from .logging import get_logger, setup_logging
from .validators import validate_pdf_file, validate_split_options

__all__ = [
    "setup_logging",
    "get_logger",
    "validate_pdf_file",
    "validate_split_options",
]
