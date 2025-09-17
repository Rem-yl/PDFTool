"""
核心处理引擎模块

提供PDF处理的核心功能，包括：
- PDF处理器
- 操作工厂
- 组件注册表
"""

from .factory import PDFOperationFactory
from .processor import PDFProcessor
from .registry import ComponentRegistry, get_global_registry

__all__ = [
    "PDFProcessor",
    "PDFOperationFactory",
    "ComponentRegistry",
    "get_global_registry",
]
