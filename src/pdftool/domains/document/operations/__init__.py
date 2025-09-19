"""
PDF Operations package
"""

from .info import InfoOperation
from .merge import MergeOperation
from .password import PasswordProtectionOperation
from .split import SplitOperation
from .watermark import WatermarkOperation

__all__ = [
    "InfoOperation",
    "MergeOperation",
    "PasswordProtectionOperation",
    "SplitOperation",
    "WatermarkOperation",
]
