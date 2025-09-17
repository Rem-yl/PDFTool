"""
组件注册表模块

提供系统级的组件注册和发现功能。
"""

from pathlib import Path
from typing import Any, Dict, List, Type

from ..common.exceptions import PDFToolError
from ..common.interfaces import IPDFOperation


class ComponentRegistry:
    """组件注册表，用于管理系统中的各种组件"""

    def __init__(self):
        self._operations: Dict[str, Type[IPDFOperation]] = {}
        self._plugins: Dict[str, Any] = {}

    def register_operation(self, name: str, operation_class: Type[IPDFOperation]) -> None:
        """注册PDF操作"""
        if name in self._operations:
            raise PDFToolError(f"Operation '{name}' already registered")
        self._operations[name] = operation_class

    def get_operation_class(self, name: str) -> Type[IPDFOperation]:
        """获取操作类"""
        if name not in self._operations:
            raise PDFToolError(f"Operation '{name}' not found")
        return self._operations[name]

    def list_operations(self) -> List[str]:
        """列出所有已注册的操作"""
        return list(self._operations.keys())

    def register_plugin(self, name: str, plugin: Any) -> None:
        """注册插件"""
        if name in self._plugins:
            raise PDFToolError(f"Plugin '{name}' already registered")
        self._plugins[name] = plugin

    def get_plugin(self, name: str) -> Any:
        """获取插件"""
        if name not in self._plugins:
            raise PDFToolError(f"Plugin '{name}' not found")
        return self._plugins[name]

    def list_plugins(self) -> List[str]:
        """列出所有已注册的插件"""
        return list(self._plugins.keys())


# 全局注册表实例
_global_registry = ComponentRegistry()


def get_global_registry() -> ComponentRegistry:
    """获取全局组件注册表"""
    return _global_registry
