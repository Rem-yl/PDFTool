"""
服务提供者实现 - 依赖注入容器
"""

from typing import Any, Callable, Dict, Type, TypeVar

from ..interfaces.processor import IServiceProvider

T = TypeVar("T")


class ServiceProvider(IServiceProvider):
    """
    简单的依赖注入容器实现
    支持单例和工厂模式
    """

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def get_service(self, service_type: Type[T]) -> T:
        """获取指定类型的服务实例"""
        # 检查是否有单例实例
        if service_type in self._singletons:
            return self._singletons[service_type]

        # 检查是否有工厂方法
        if service_type in self._factories:
            instance = self._factories[service_type]()
            # 如果是单例，缓存实例
            if hasattr(instance.__class__, "_singleton") and getattr(
                instance.__class__, "_singleton"
            ):
                self._singletons[service_type] = instance
            return instance

        # 检查是否有直接注册的服务
        if service_type in self._services:
            return self._services[service_type]

        raise ValueError(f"Service not registered: {service_type}")

    def register_service(self, service_type: Type, service_instance: Any) -> None:
        """注册服务实例"""
        self._services[service_type] = service_instance

    def register_factory(self, service_type: Type, factory: Callable) -> None:
        """注册服务工厂方法"""
        self._factories[service_type] = factory

    def register_singleton(self, service_type: Type, service_instance: Any) -> None:
        """注册单例服务"""
        self._singletons[service_type] = service_instance

    def has_service(self, service_type: Type) -> bool:
        """检查是否已注册指定类型的服务"""
        return (
            service_type in self._services
            or service_type in self._factories
            or service_type in self._singletons
        )

    def clear_services(self) -> None:
        """清除所有注册的服务"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()


# 全局服务提供者实例
_global_service_provider = ServiceProvider()


def get_service_provider() -> ServiceProvider:
    """获取全局服务提供者实例"""
    return _global_service_provider


def register_service(service_type: Type, service_instance: Any) -> None:
    """快捷方法：注册服务到全局服务提供者"""
    _global_service_provider.register_service(service_type, service_instance)


def register_factory(service_type: Type, factory: Callable) -> None:
    """快捷方法：注册工厂方法到全局服务提供者"""
    _global_service_provider.register_factory(service_type, factory)


def register_singleton(service_type: Type, service_instance: Any) -> None:
    """快捷方法：注册单例服务到全局服务提供者"""
    _global_service_provider.register_singleton(service_type, service_instance)


def get_service(service_type: Type[T]) -> T:
    """快捷方法：从全局服务提供者获取服务"""
    return _global_service_provider.get_service(service_type)
