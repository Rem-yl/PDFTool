"""
通用操作执行器实现
"""

from typing import Any, Dict, List, Optional, Type

from ..interfaces.processor import IOperationExecutor
from ..utils.logging import get_logger

logger = get_logger("operation_executor")


class PluggableOperationExecutor(IOperationExecutor):
    """
    可插拔的操作执行器
    支持动态注册和执行各种类型的操作
    """

    def __init__(self):
        """初始化操作执行器"""
        self._operations: Dict[str, Type] = {}
        self._operation_instances: Dict[str, Any] = {}
        logger.info("操作执行器初始化完成")

    def execute(
        self, operation_type: str, input_data: Any, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        执行指定类型的操作

        Args:
            operation_type: 操作类型名称
            input_data: 输入数据
            options: 操作选项

        Returns:
            操作结果

        Raises:
            ValueError: 当操作类型不存在时
            RuntimeError: 当操作执行失败时
        """
        if operation_type not in self._operations:
            available_ops = ", ".join(self._operations.keys())
            raise ValueError(f"Unknown operation: {operation_type}. Available: {available_ops}")

        try:
            # 获取或创建操作实例
            operation_instance = self._get_operation_instance(operation_type)

            # 执行操作
            if hasattr(operation_instance, "execute"):
                result = operation_instance.execute(input_data, options)
            elif callable(operation_instance):
                result = operation_instance(input_data, options)
            else:
                raise RuntimeError(f"Operation {operation_type} is not executable")

            logger.info(f"操作执行成功: {operation_type}")
            return result

        except Exception as e:
            logger.error(f"操作执行失败 {operation_type}: {str(e)}")
            raise RuntimeError(f"Operation execution failed: {str(e)}")

    def get_supported_operations(self) -> List[str]:
        """获取支持的操作类型列表"""
        return list(self._operations.keys())

    def register_operation(self, operation_type: str, operation_class: Any) -> None:
        """
        注册新的操作类型

        Args:
            operation_type: 操作类型名称
            operation_class: 操作类、实例或可调用对象
        """
        self._operations[operation_type] = operation_class
        # 清除已缓存的实例
        if operation_type in self._operation_instances:
            del self._operation_instances[operation_type]

        logger.info(f"注册操作类型: {operation_type} -> {operation_class.__name__}")

    def unregister_operation(self, operation_type: str) -> None:
        """注销操作类型"""
        if operation_type in self._operations:
            del self._operations[operation_type]
            if operation_type in self._operation_instances:
                del self._operation_instances[operation_type]
            logger.info(f"注销操作类型: {operation_type}")

    def has_operation(self, operation_type: str) -> bool:
        """检查是否支持指定的操作类型"""
        return operation_type in self._operations

    def _get_operation_instance(self, operation_type: str) -> Any:
        """获取操作实例（支持单例模式）"""
        if operation_type not in self._operation_instances:
            operation_class_or_instance = self._operations[operation_type]

            # 如果已经是实例，直接使用
            if not isinstance(operation_class_or_instance, type):
                instance = operation_class_or_instance
            else:
                # 检查是否需要依赖注入
                operation_class = operation_class_or_instance
                if hasattr(operation_class, "__init__"):
                    try:
                        # 尝试无参数实例化
                        instance = operation_class()
                    except TypeError:
                        # 如果需要参数，尝试从服务提供者获取
                        from .service_provider import get_service_provider

                        service_provider = get_service_provider()

                        # 简单的依赖注入
                        init_signature = getattr(operation_class.__init__, "__annotations__", {})
                        init_args = {}

                        for param_name, param_type in init_signature.items():
                            if param_name != "return" and service_provider.has_service(param_type):
                                init_args[param_name] = service_provider.get_service(param_type)

                        instance = operation_class(**init_args)
                else:
                    instance = operation_class

            self._operation_instances[operation_type] = instance

        return self._operation_instances[operation_type]

    def clear_instances(self) -> None:
        """清除所有已缓存的操作实例"""
        self._operation_instances.clear()
        logger.info("清除所有操作实例缓存")

    def get_operation_info(self, operation_type: str) -> Dict[str, Any]:
        """获取操作信息"""
        if operation_type not in self._operations:
            raise ValueError(f"Unknown operation: {operation_type}")

        operation_class = self._operations[operation_type]
        return {
            "type": operation_type,
            "class": operation_class.__name__,
            "module": operation_class.__module__,
            "doc": operation_class.__doc__,
            "methods": [method for method in dir(operation_class) if not method.startswith("_")],
        }


class CompositeOperationExecutor(IOperationExecutor):
    """
    组合操作执行器
    支持将多个执行器组合使用
    """

    def __init__(self):
        """初始化组合执行器"""
        self._executors: List[IOperationExecutor] = []
        logger.info("组合操作执行器初始化完成")

    def add_executor(self, executor: IOperationExecutor) -> None:
        """添加子执行器"""
        self._executors.append(executor)
        logger.info(f"添加子执行器: {executor.__class__.__name__}")

    def remove_executor(self, executor: IOperationExecutor) -> None:
        """移除子执行器"""
        if executor in self._executors:
            self._executors.remove(executor)
            logger.info(f"移除子执行器: {executor.__class__.__name__}")

    def execute(
        self, operation_type: str, input_data: Any, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """在子执行器中查找并执行操作"""
        for executor in self._executors:
            if operation_type in executor.get_supported_operations():
                return executor.execute(operation_type, input_data, options)

        available_ops = ", ".join(self.get_supported_operations())
        raise ValueError(f"Unknown operation: {operation_type}. Available: {available_ops}")

    def get_supported_operations(self) -> List[str]:
        """获取所有子执行器支持的操作类型"""
        operations = set()
        for executor in self._executors:
            operations.update(executor.get_supported_operations())
        return list(operations)

    def register_operation(self, operation_type: str, operation_class: Type) -> None:
        """在第一个支持注册的子执行器中注册操作"""
        for executor in self._executors:
            if hasattr(executor, "register_operation"):
                executor.register_operation(operation_type, operation_class)
                return

        raise RuntimeError("No executor supports operation registration")


class ChainedOperationExecutor(IOperationExecutor):
    """
    链式操作执行器
    支持将多个操作组合成链式执行
    """

    def __init__(self, base_executor: IOperationExecutor):
        """初始化链式执行器"""
        self.base_executor = base_executor
        self._chains: Dict[str, List[str]] = {}

    def define_chain(self, chain_name: str, operations: List[str]) -> None:
        """定义操作链"""
        self._chains[chain_name] = operations
        logger.info(f"定义操作链 {chain_name}: {' -> '.join(operations)}")

    def execute(
        self, operation_type: str, input_data: Any, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """执行操作或操作链"""
        if operation_type in self._chains:
            # 执行操作链
            result = input_data
            for op in self._chains[operation_type]:
                result = self.base_executor.execute(op, result, options)
            return result
        else:
            # 执行单个操作
            return self.base_executor.execute(operation_type, input_data, options)

    def get_supported_operations(self) -> List[str]:
        """获取支持的操作类型（包括操作链）"""
        ops = self.base_executor.get_supported_operations()
        ops.extend(self._chains.keys())
        return ops

    def register_operation(self, operation_type: str, operation_class: Type) -> None:
        """委托给基础执行器"""
        self.base_executor.register_operation(operation_type, operation_class)
