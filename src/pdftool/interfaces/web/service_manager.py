"""
解耦的服务管理器 - 新的可扩展架构
"""

from pathlib import Path
from typing import Any, Dict, Optional, Type

from ...common.interfaces.processor import (
    IOperationExecutor,
    IResourceManager,
    IServiceProvider,
)
from ...common.services.operation_executor import PluggableOperationExecutor
from ...common.services.resource_manager import FileResourceManager
from ...common.services.service_provider import ServiceProvider
from .service_registry import ServiceRegistry


class ServiceManager:
    """
    解耦的API服务管理器
    使用依赖注入和服务定位器模式
    """

    def __init__(
        self, temp_dir: Optional[Path] = None, service_provider: Optional[IServiceProvider] = None
    ):
        """
        初始化服务管理器

        Args:
            temp_dir: 临时目录路径
            service_provider: 可选的自定义服务提供者
        """
        self.service_provider = service_provider or ServiceProvider()
        self.temp_dir = temp_dir or Path("temp")

        # 初始化核心服务
        self._initialize_core_services()

        # 初始化服务注册表
        self.service_registry = ServiceRegistry(service_provider=self.service_provider)

    def _initialize_core_services(self) -> None:
        """初始化核心服务并注册到服务提供者"""
        # 创建资源管理器
        resource_manager = FileResourceManager(temp_dir=self.temp_dir)
        if hasattr(self.service_provider, "register_singleton"):
            self.service_provider.register_singleton(IResourceManager, resource_manager)
        else:
            self.service_provider.register_service(IResourceManager, resource_manager)

        # 创建操作执行器
        operation_executor = PluggableOperationExecutor()
        if hasattr(self.service_provider, "register_singleton"):
            self.service_provider.register_singleton(IOperationExecutor, operation_executor)
        else:
            self.service_provider.register_service(IOperationExecutor, operation_executor)

        # 注册PDF操作类
        self._register_pdf_operations(operation_executor)

    def _register_pdf_operations(self, operation_executor: IOperationExecutor) -> None:
        """注册PDF操作类到操作执行器 - 新架构版本"""
        try:
            from ...domains.document.operations.info import InfoOperation
            from ...domains.document.operations.merge import MergeOperation
            from ...domains.document.operations.split import SplitOperation
            from ...domains.document.operations.watermark import WatermarkOperation

            operation_executor.register_operation("merge", MergeOperation)
            operation_executor.register_operation("split", SplitOperation)
            operation_executor.register_operation("info", InfoOperation)
            operation_executor.register_operation("watermark", WatermarkOperation)

            from ...common.utils.logging import get_logger

            logger = get_logger("service_manager")
            logger.info("成功注册所有PDF操作类")

        except ImportError as e:
            from ...common.utils.logging import get_logger

            logger = get_logger("service_manager")
            logger.error(f"无法导入PDF操作类: {e}")
            raise RuntimeError(f"PDF操作类导入失败，请检查架构配置: {e}")
        except Exception as e:
            from ...common.utils.logging import get_logger

            logger = get_logger("service_manager")
            logger.error(f"注册PDF操作类时发生错误: {e}")
            raise

    def get_service_handler(self, service_name: str):
        """获取服务处理器"""
        return self.service_registry.get_handler(service_name)

    def register_service(
        self, service_name: str, handler_class: type, dependencies: Optional[Dict[str, Type]] = None
    ) -> None:
        """
        注册新的服务处理器

        Args:
            service_name: 服务名称
            handler_class: 处理器类
            dependencies: 依赖项映射
        """
        self.service_registry.register_handler(service_name, handler_class, dependencies)

    def list_available_services(self) -> list[str]:
        """列出所有可用服务"""
        return self.service_registry.list_services()

    def register_operation(self, operation_type: str, operation_class: type) -> None:
        """注册新的PDF操作"""
        operation_executor = self.service_provider.get_service(IOperationExecutor)
        operation_executor.register_operation(operation_type, operation_class)

    def list_available_operations(self) -> list[str]:
        """列出所有可用操作"""
        operation_executor = self.service_provider.get_service(IOperationExecutor)
        return operation_executor.get_supported_operations()

    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """获取服务信息"""
        return self.service_registry.get_service_info(service_name)

    def get_operation_executor(self) -> IOperationExecutor:
        """获取操作执行器"""
        return self.service_provider.get_service(IOperationExecutor)

    def get_resource_manager(self) -> IResourceManager:
        """获取资源管理器"""
        return self.service_provider.get_service(IResourceManager)

    def register_custom_service(self, service_type: Type, service_instance: Any) -> None:
        """注册自定义服务到服务提供者"""
        self.service_provider.register_service(service_type, service_instance)

    def configure_services(self, config: Dict[str, Any]) -> None:
        """根据配置设置服务"""
        # 可以根据配置动态调整服务设置
        if "max_file_size" in config:
            # 设置最大文件大小等配置
            pass

        if "additional_operations" in config:
            # 注册额外的操作
            operation_executor = self.get_operation_executor()
            for op_name, op_class in config["additional_operations"].items():
                operation_executor.register_operation(op_name, op_class)

    def cleanup(self) -> None:
        """清理资源"""
        try:
            resource_manager = self.get_resource_manager()
            # 可以添加全局清理逻辑
            if hasattr(resource_manager, "cleanup_resources"):
                # 获取需要清理的资源（如果有的话）
                # 这里可以根据实际需要实现具体的清理逻辑
                resource_manager.cleanup_resources([])
        except (AttributeError, RuntimeError) as e:
            # 记录清理错误但不中断程序
            from ...common.utils.logging import get_logger

            logger = get_logger("service_manager")
            logger.warning(f"资源清理失败: {e}")
