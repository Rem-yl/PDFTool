"""
解耦的服务管理器 - 新的可扩展架构
"""

from pathlib import Path
from typing import Any, Dict, Optional, Type

from ...common.utils.logging import get_logger
from .service_registry import ServiceRegistry

# Note: IServiceProvider interface was removed, using basic service management


logger = get_logger("service_manager")


class ServiceManager:
    """
    解耦的API服务管理器
    使用依赖注入和服务定位器模式
    """

    def __init__(self, temp_dir: Optional[Path] = None, service_provider: Optional[Any] = None):
        """
        初始化服务管理器

        Args:
            temp_dir: 临时目录路径
            service_provider: 可选的自定义服务提供者
        """
        self.temp_dir = temp_dir or Path("temp")
        # 初始化服务注册表, web ui所有的服务都在这里
        self.service_registry = ServiceRegistry()

    def get_service_handler(self, service_name: str):
        """获取服务处理器"""
        return self.service_registry.get_handler(service_name)

    def register_service(self, service_name: str, handler_class: type) -> None:
        """
        注册新的服务处理器

        Args:
            service_name: 服务名称
            handler_class: 处理器类
            dependencies: 依赖项映射
        """
        self.service_registry.register_handler(service_name, handler_class)

    def list_available_services(self) -> list[str]:
        """列出所有可用服务"""
        return self.service_registry.list_services()

    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """获取服务信息"""
        return self.service_registry.get_service_info(service_name)

    def cleanup(self) -> None:
        """清理资源"""
        try:
            resource_manager = self.get_resource_manager()
            if hasattr(resource_manager, "cleanup_resources"):
                resource_manager.cleanup_resources([])
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"资源清理失败: {e}")
