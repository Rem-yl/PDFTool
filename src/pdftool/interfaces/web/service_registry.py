"""
Service registry for API handlers - Decoupled architecture
"""

from typing import Any, Dict, Type

from ...common.utils.logging import get_logger
from .interfaces import BaseServiceHandler, IServiceRegistry

logger = get_logger(__name__)


class ServiceRegistry(IServiceRegistry):
    """
    解耦的服务注册表
    使用依赖注入而不是直接依赖具体的处理器类
    """

    def __init__(self):
        """
        初始化服务注册表
        """
        self._handlers: Dict[str, Type[BaseServiceHandler]] = {}
        self._handler_dependencies: Dict[str, Dict] = {}
        self.register_service_handlers()

    def register_handler(
        self,
        service_name: str,
        handler_class: Type[BaseServiceHandler],
    ) -> None:
        """
        注册服务处理器

        Args:
            service_name: 服务名称
            handler_class: 处理器类
            dependencies: 依赖项映射
        """
        if service_name in self._handlers:
            logger.warning(f"Service {service_name} already registered.")
        else:
            self._handlers[service_name] = handler_class
            logger.info(f"Service: {service_name} has been registered.")

    def get_handler(self, service_name: str) -> BaseServiceHandler:
        """
        获取服务处理器实例

        Args:
            service_name: 服务名称

        Returns:
            服务处理器实例

        Raises:
            ValueError: 当服务不存在时
        """
        if service_name not in self._handlers:
            available = ", ".join(self._handlers.keys())
            raise ValueError(f"Unknown service: {service_name}. Available: {available}")

        handler_class = self._handlers[service_name]

        try:
            return handler_class()
        except Exception as e:
            raise RuntimeError(f"Failed to create handler for {service_name}: {str(e)}")

    def list_services(self) -> list[str]:
        """列出所有已注册的服务"""
        return list(self._handlers.keys())

    def has_service(self, service_name: str) -> bool:
        """检查服务是否已注册"""
        return service_name in self._handlers

    def unregister_handler(self, service_name: str) -> None:
        """注销服务处理器"""
        if service_name in self._handlers:
            del self._handlers[service_name]
            if service_name in self._handler_dependencies:
                del self._handler_dependencies[service_name]

    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """获取服务信息"""
        if service_name not in self._handlers:
            raise ValueError(f"Unknown service: {service_name}")

        handler_class = self._handlers[service_name]

        return {
            "name": service_name,
            "class": handler_class.__name__,
            "module": handler_class.__module__,
            "doc": handler_class.__doc__ or "No documentation",
        }

    def register_service_handlers(self) -> None:
        """注册默认的服务处理器"""
        # 定义服务列表，包含服务名和对应的处理器类
        services = [
            ("merge", "MergeServiceHandler"),
            ("split", "SplitServiceHandler"),
            ("info", "InfoServiceHandler"),
            ("watermark", "WatermarkServiceHandler"),
        ]

        for service_name, handler_class_name in services:
            try:
                # 使用绝对导入路径
                module_path = f"pdftool.interfaces.web.handlers.{service_name}"
                module = __import__(module_path, fromlist=[handler_class_name])
                handler_class = getattr(module, handler_class_name)

                # 注册处理器
                self.register_handler(service_name, handler_class)

            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to register service {service_name}: {e}")
