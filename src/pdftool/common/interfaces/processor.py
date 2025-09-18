"""
通用处理器接口定义
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, TypeVar

# 类型变量
T = TypeVar("T")
R = TypeVar("R")


class IDataProcessor(Protocol[T, R]):
    """通用数据处理器协议"""

    def process(self, input_data: T, options: Optional[Dict[str, Any]] = None) -> R:
        """处理输入数据并返回结果"""
        ...


class IAsyncDataProcessor(Protocol[T, R]):
    """异步数据处理器协议"""

    async def process(self, input_data: T, options: Optional[Dict[str, Any]] = None) -> R:
        """异步处理输入数据并返回结果"""
        ...


class IProcessorFactory(ABC):
    """处理器工厂接口"""

    @abstractmethod
    def create_processor(self, processor_type: str, **kwargs) -> Any:
        """创建指定类型的处理器"""
        pass

    @abstractmethod
    def register_processor(self, processor_type: str, processor_class: type) -> None:
        """注册新的处理器类型"""
        pass

    @abstractmethod
    def list_processor_types(self) -> List[str]:
        """列出所有可用的处理器类型"""
        pass


class IOperationExecutor(ABC):
    """操作执行器接口 - 负责执行具体的业务操作"""

    @abstractmethod
    def execute(
        self, operation_type: str, input_data: Any, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行指定类型的操作"""
        pass

    @abstractmethod
    def get_supported_operations(self) -> List[str]:
        """获取支持的操作类型列表"""
        pass

    @abstractmethod
    def register_operation(self, operation_type: str, operation_class: type) -> None:
        """注册新的操作类型"""
        pass


class IResourceManager(ABC):
    """资源管理器接口 - 负责临时文件、清理等"""

    @abstractmethod
    def create_temp_file(self, suffix: str = "", prefix: str = "temp") -> Any:
        """创建临时文件"""
        pass

    @abstractmethod
    def create_temp_dir(self, prefix: str = "temp") -> Any:
        """创建临时目录"""
        pass

    @abstractmethod
    def cleanup_resources(self, resources: List[Any]) -> None:
        """清理资源"""
        pass

    @abstractmethod
    def create_archive(self, files: List[Any], output_path: Optional[Any] = None) -> Any:
        """创建归档文件"""
        pass


class IServiceProvider(ABC):
    """服务提供者接口 - 松耦合的服务定位器"""

    @abstractmethod
    def get_service(self, service_type: type[T]) -> T:
        """获取指定类型的服务实例"""
        pass

    @abstractmethod
    def register_service(self, service_type: type, service_instance: Any) -> None:
        """注册服务实例"""
        pass

    @abstractmethod
    def has_service(self, service_type: type) -> bool:
        """检查是否已注册指定类型的服务"""
        pass


class IConfigurationProvider(ABC):
    """配置提供者接口"""

    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass

    @abstractmethod
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        pass


class BasePDFOperation(ABC):
    """PDF操作基类 - 所有PDF操作的基础接口"""

    @property
    @abstractmethod
    def operation_type(self) -> str:
        """操作类型标识符"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """操作的显示名称"""
        pass

    @abstractmethod
    def execute(self, input_files: List[Path], options: Optional[Dict[str, Any]] = None) -> Any:
        """执行PDF操作

        Args:
            input_files: 输入文件路径列表
            options: 操作选项

        Returns:
            操作结果
        """
        pass

    def validate_input(
        self, input_files: List[Path], options: Optional[Dict[str, Any]] = None
    ) -> None:
        """验证输入参数

        Args:
            input_files: 输入文件路径列表
            options: 操作选项

        Raises:
            ValidationError: 当输入无效时
        """
        if not input_files:
            raise ValueError("至少需要一个输入文件")

        for file_path in input_files:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            if not file_path.suffix.lower() == ".pdf":
                raise ValueError(f"文件不是PDF格式: {file_path}")
