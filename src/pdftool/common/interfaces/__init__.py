"""
通用接口包
"""

from .processor import (
    BasePDFOperation,
    IAsyncDataProcessor,
    IConfigurationProvider,
    IDataProcessor,
    IOperationExecutor,
    IProcessorFactory,
    IResourceManager,
    IServiceProvider,
)

__all__ = [
    "IDataProcessor",
    "IAsyncDataProcessor",
    "IProcessorFactory",
    "IOperationExecutor",
    "IResourceManager",
    "IServiceProvider",
    "IConfigurationProvider",
    "BasePDFOperation",
]
