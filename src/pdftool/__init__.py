"""
PDFTool - A comprehensive PDF manipulation library

This package provides tools for PDF merging, splitting, and information extraction
through both programmatic APIs and user interfaces (CLI, GUI, Web).
"""

__version__ = "1.0.0"
__author__ = "PDFTool Team"
__email__ = "contact@pdftool.com"

from .core.exceptions import PDFProcessingError, PDFToolError, PDFValidationError
from .core.pdf_operations import PDFOperations

__all__ = ["PDFOperations", "PDFToolError", "PDFValidationError", "PDFProcessingError"]
