"""
PDFTool - A comprehensive PDF manipulation library

This package provides tools for PDF merging, splitting, watermarking, and information extraction
through both programmatic APIs and user interfaces (CLI, Web).

Domain-driven plugin architecture enables easy extension with custom operations.
"""

__version__ = "1.0.0"
__author__ = "PDFTool Team"
__email__ = "contact@pdftool.com"

# Common Components
from .common.exceptions import PDFProcessingError, PDFToolError, PDFValidationError
from .common.interfaces import BasePDFOperation, IPDFOperation

# Core Components
from .core.factory import PDFOperationFactory
from .core.processor import PDFProcessor
from .core.registry import ComponentRegistry

__all__ = [
    # Core processing
    "PDFProcessor",
    "PDFOperationFactory",
    "ComponentRegistry",
    # Interfaces for extension
    "IPDFOperation",
    "BasePDFOperation",
    # Exceptions
    "PDFToolError",
    "PDFValidationError",
    "PDFProcessingError",
]
