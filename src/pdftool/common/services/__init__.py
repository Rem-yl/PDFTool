"""
通用服务包
"""

from .operation_executor import (
    ChainedOperationExecutor,
    CompositeOperationExecutor,
    PluggableOperationExecutor,
)
from .resource_manager import FileResourceManager, MemoryResourceManager
from .service_provider import (
    ServiceProvider,
    get_service,
    get_service_provider,
    register_factory,
    register_service,
    register_singleton,
)

__all__ = [
    "ServiceProvider",
    "get_service_provider",
    "get_service",
    "register_service",
    "register_factory",
    "register_singleton",
    "FileResourceManager",
    "MemoryResourceManager",
    "PluggableOperationExecutor",
    "CompositeOperationExecutor",
    "ChainedOperationExecutor",
]
