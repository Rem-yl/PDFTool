"""
PDFTool - A comprehensive PDF manipulation library

This package provides tools for PDF merging, splitting, watermarking, and information extraction
through both programmatic APIs and user interfaces (CLI, Web).

Domain-driven plugin architecture enables easy extension with custom operations.
"""

__version__ = "1.0.0"
__author__ = "PDFTool Team"
__email__ = "contact@pdftool.com"

# Common Components - New Architecture Only
from .common.exceptions import PDFProcessingError, PDFToolError, PDFValidationError
from .common.interfaces.processor import (
    IDataProcessor,
    IOperationExecutor,
    IResourceManager,
    IServiceProvider,
)
from .common.services.operation_executor import PluggableOperationExecutor
from .common.services.resource_manager import FileResourceManager

# Services
from .common.services.service_provider import ServiceProvider

__all__ = [
    # New Architecture Interfaces
    "IDataProcessor",
    "IOperationExecutor",
    "IResourceManager",
    "IServiceProvider",
    # Services Implementation
    "ServiceProvider",
    "PluggableOperationExecutor",
    "FileResourceManager",
    # Exceptions
    "PDFToolError",
    "PDFValidationError",
    "PDFProcessingError",
]
