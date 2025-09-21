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
    from .watermark import WatermarkOperation
    __all__.append("WatermarkOperation")
except ImportError:
    pass

try:
    from .conversion_ocr import ConversionOperationOCR
    __all__.append("ConversionOperationOCR")
except ImportError:
    pass
