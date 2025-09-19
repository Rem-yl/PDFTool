"""
Web接口模块

提供基于FastAPI的Web接口功能。
"""

from .application import app
from .main import main
from .service_registry import ServiceRegistry

__all__ = [
    "app",
    "main",
    "ServiceRegistry",
]
