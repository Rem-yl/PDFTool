"""
PDF Operations package
"""

from .conversion import ConversionOperation
from .info import InfoOperation
from .merge import MergeOperation
from .password import PasswordProtectionOperation
from .split import SplitOperation

__all__ = [
    "ConversionOperation",
    "InfoOperation",
    "MergeOperation",
    "PasswordProtectionOperation",
    "SplitOperation",
]

# Conditionally import operations that require PIL/external dependencies
try:
    from .watermark import WatermarkOperation  # noqa: F401

    __all__.append("WatermarkOperation")
except ImportError:
    pass

# ConversionOperation already imported above, no need to re-import
