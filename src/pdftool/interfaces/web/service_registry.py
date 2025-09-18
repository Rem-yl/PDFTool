"""
Service registry for API handlers - Decoupled architecture
"""

from typing import Dict, Optional, Type

from ...common.interfaces.processor import IServiceProvider
from ...common.services.service_provider import get_service_provider
from .interfaces import IServiceHandler, IServiceRegistry


class ServiceRegistry(IServiceRegistry):
    """
    解耦的服务注册表
    使用依赖注入而不是直接依赖具体的处理器类
    """

    def __init__(self, service_provider: Optional[IServiceProvider] = None):
        """
        初始化服务注册表

        Args:
            service_provider: 依赖注入容器，如果为None则使用全局服务提供者
        """
        self.service_provider = service_provider or get_service_provider()
        self._handlers: Dict[str, Type[IServiceHandler]] = {}
        self._handler_dependencies: Dict[str, Dict[str, Type]] = {}
        self._register_default_handlers()

    def register_handler(
        self,
        service_name: str,
        handler_class: Type[IServiceHandler],
        dependencies: Optional[Dict[str, Type]] = None,
    ) -> None:
        """
        注册服务处理器

        Args:
            service_name: 服务名称
            handler_class: 处理器类
            dependencies: 处理器依赖的服务类型映射
        """
        self._handlers[service_name] = handler_class
        self._handler_dependencies[service_name] = dependencies or {}

    def get_handler(self, service_name: str) -> IServiceHandler:
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
        dependencies = self._handler_dependencies.get(service_name, {})

        # 解析依赖并创建实例
        resolved_dependencies = {}
        for dep_name, dep_type in dependencies.items():
            if self.service_provider.has_service(dep_type):
                resolved_dependencies[dep_name] = self.service_provider.get_service(dep_type)
            else:
                raise RuntimeError(
                    f"Required dependency {dep_type} not found for service {service_name}"
                )

        # 创建处理器实例
        try:
            return handler_class(**resolved_dependencies)
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

    def get_service_info(self, service_name: str) -> Dict[str, any]:
        """获取服务信息"""
        if service_name not in self._handlers:
            raise ValueError(f"Unknown service: {service_name}")

        handler_class = self._handlers[service_name]
        dependencies = self._handler_dependencies.get(service_name, {})

        return {
            "name": service_name,
            "class": handler_class.__name__,
            "module": handler_class.__module__,
            "doc": handler_class.__doc__ or "No documentation",
            "dependencies": list(dependencies.keys()),
        }

    def _register_default_handlers(self) -> None:
        """注册默认的服务处理器"""
        # 导入这里以避免循环导入
        from ...common.interfaces.processor import IOperationExecutor, IResourceManager

        try:
            from .handlers.info import InfoServiceHandler
            from .handlers.merge import MergeServiceHandler
            from .handlers.split import SplitServiceHandler
            from .handlers.watermark import WatermarkServiceHandler

            # 定义每个处理器的依赖, 类似于给每个Handler赋予操作执行器
            common_dependencies = {
                "operation_executor": IOperationExecutor,
                "resource_manager": IResourceManager,
            }

            self.register_handler("merge", MergeServiceHandler, common_dependencies)
            self.register_handler("split", SplitServiceHandler, common_dependencies)
            self.register_handler("info", InfoServiceHandler, common_dependencies)
            self.register_handler("watermark", WatermarkServiceHandler, common_dependencies)

        except ImportError:
            # 如果处理器类不存在，跳过注册
            pass
