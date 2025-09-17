"""
插件加载器

负责动态加载和管理插件。
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..common.exceptions import PDFToolError
from .base import BasePlugin
from .registry import PluginRegistry


class PluginLoader:
    """插件加载器"""

    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()
        self._loaded_plugins: Dict[str, BasePlugin] = {}

    def load_plugin_from_module(self, module_name: str, plugin_class_name: str) -> BasePlugin:
        """从模块加载插件"""
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, plugin_class_name)

            if not issubclass(plugin_class, BasePlugin):
                raise PDFToolError(f"Plugin class {plugin_class_name} must inherit from BasePlugin")

            plugin = plugin_class()
            self.registry.register_plugin(plugin)
            self._loaded_plugins[plugin.name] = plugin

            return plugin

        except ImportError as e:
            raise PDFToolError(f"Failed to import module {module_name}: {e}")
        except AttributeError as e:
            raise PDFToolError(
                f"Plugin class {plugin_class_name} not found in module {module_name}: {e}"
            )

    def load_plugins_from_directory(self, plugin_dir: Path) -> List[BasePlugin]:
        """从目录加载所有插件"""
        loaded_plugins = []

        if not plugin_dir.exists() or not plugin_dir.is_dir():
            return loaded_plugins

        for finder, name, ispkg in pkgutil.iter_modules([str(plugin_dir)]):
            try:
                module = finder.find_module(name).load_module(name)

                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr != BasePlugin
                    ):

                        plugin = attr()
                        self.registry.register_plugin(plugin)
                        self._loaded_plugins[plugin.name] = plugin
                        loaded_plugins.append(plugin)
                        break

            except Exception as e:
                # 跳过加载失败的插件
                continue

        return loaded_plugins

    def initialize_plugins(self, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化所有已加载的插件"""
        for plugin in self._loaded_plugins.values():
            try:
                plugin.initialize(config)
            except Exception as e:
                # 记录错误但继续初始化其他插件
                pass

    def shutdown_plugins(self) -> None:
        """关闭所有插件"""
        for plugin in self._loaded_plugins.values():
            try:
                plugin.shutdown()
            except Exception as e:
                # 记录错误但继续关闭其他插件
                pass

    def get_loaded_plugin(self, name: str) -> Optional[BasePlugin]:
        """获取已加载的插件"""
        return self._loaded_plugins.get(name)

    def list_loaded_plugins(self) -> List[str]:
        """列出所有已加载的插件名称"""
        return list(self._loaded_plugins.keys())
