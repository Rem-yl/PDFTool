"""
插件基类

定义插件的基础结构和接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BasePlugin(ABC):
    """插件基类"""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._config: Dict[str, Any] = {}

    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化插件"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭插件"""
        pass

    def configure(self, config: Dict[str, Any]) -> None:
        """配置插件"""
        self._config.update(config)

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} v{self.version}>"
