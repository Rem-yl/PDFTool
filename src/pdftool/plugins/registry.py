"""
插件注册表

管理插件的注册、发现和生命周期。
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Type

from ..common.exceptions import PDFToolError
from .base import BasePlugin


class PluginRegistry:
    """插件注册表"""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugins_by_type: Dict[str, List[BasePlugin]] = defaultdict(list)
        self._plugin_metadata: Dict[str, Dict[str, Any]] = {}

    def register_plugin(self, plugin: BasePlugin, plugin_type: str = "general") -> None:
        """注册插件"""
        if plugin.name in self._plugins:
            raise PDFToolError(f"Plugin '{plugin.name}' already registered")

        self._plugins[plugin.name] = plugin
        self._plugins_by_type[plugin_type].append(plugin)
        self._plugin_metadata[plugin.name] = {
            "type": plugin_type,
            "version": plugin.version,
            "description": plugin.description,
        }

    def unregister_plugin(self, name: str) -> None:
        """注销插件"""
        if name not in self._plugins:
            raise PDFToolError(f"Plugin '{name}' not found")

        plugin = self._plugins[name]
        plugin_type = self._plugin_metadata[name]["type"]

        # 关闭插件
        try:
            plugin.shutdown()
        except Exception:
            pass

        # 从注册表中移除
        del self._plugins[name]
        del self._plugin_metadata[name]
        self._plugins_by_type[plugin_type].remove(plugin)

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """获取插件"""
        return self._plugins.get(name)

    def get_plugins_by_type(self, plugin_type: str) -> List[BasePlugin]:
        """根据类型获取插件列表"""
        return self._plugins_by_type.get(plugin_type, [])

    def list_plugins(self) -> List[str]:
        """列出所有插件名称"""
        return list(self._plugins.keys())

    def list_plugin_types(self) -> List[str]:
        """列出所有插件类型"""
        return list(self._plugins_by_type.keys())

    def get_plugin_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """获取插件元数据"""
        return self._plugin_metadata.get(name)

    def list_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """获取所有插件的元数据"""
        return self._plugin_metadata.copy()

    def is_plugin_registered(self, name: str) -> bool:
        """检查插件是否已注册"""
        return name in self._plugins

    def get_plugin_count(self) -> int:
        """获取插件总数"""
        return len(self._plugins)

    def get_plugin_count_by_type(self, plugin_type: str) -> int:
        """获取指定类型的插件数量"""
        return len(self._plugins_by_type.get(plugin_type, []))

    def clear_all(self) -> None:
        """清空所有插件"""
        # 关闭所有插件
        for plugin in self._plugins.values():
            try:
                plugin.shutdown()
            except Exception:
                pass

        # 清空注册表
        self._plugins.clear()
        self._plugins_by_type.clear()
        self._plugin_metadata.clear()


# 全局插件注册表实例
_global_plugin_registry = PluginRegistry()


def get_global_plugin_registry() -> PluginRegistry:
    """获取全局插件注册表"""
    return _global_plugin_registry
