"""
PDFTool - A comprehensive PDF manipulation library

This package provides tools for PDF merging, splitting, watermarking, and information extraction
through both programmatic APIs and user interfaces (CLI, GUI, Web).

New plugin-based architecture enables easy extension with custom operations.
"""

__version__ = "1.0.0"
__author__ = "PDFTool Team"
__email__ = "contact@pdftool.com"

# API Components
from .api.service_manager import ServiceManager

# Core Components
from .core.exceptions import PDFProcessingError, PDFToolError, PDFValidationError
from .core.interfaces import BasePDFOperation, IPDFOperation
from .core.operation_factory import PDFOperationFactory
from .core.pdf_processor import PDFProcessor

__all__ = [
    # Core processing
    "PDFProcessor",
    "PDFOperationFactory",
    # Interfaces for extension
    "IPDFOperation",
    "BasePDFOperation",
    # API Management
    "ServiceManager",
    # Exceptions
    "PDFToolError",
    "PDFValidationError",
    "PDFProcessingError",
]
