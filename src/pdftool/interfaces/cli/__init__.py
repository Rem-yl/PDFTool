"""
命令行接口模块

提供PDFTool的命令行接口功能。
"""

from .commands import create_cli_app
from .main import main

__all__ = [
    "create_cli_app",
    "main",
]
