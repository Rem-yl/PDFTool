"""
Web接口模块

提供基于FastAPI的Web接口功能。
"""

from .application import app
from .main import main
from .service_manager import ServiceManager

__all__ = [
    "app",
    "main",
    "ServiceManager",
]
