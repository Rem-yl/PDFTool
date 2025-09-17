"""
Custom exceptions for PDFTool operations
"""

from typing import Optional


class PDFToolError(Exception):
    """Base exception class for PDFTool operations"""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class PDFValidationError(PDFToolError):
    """Raised when PDF validation fails"""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class PDFProcessingError(PDFToolError):
    """Raised when PDF processing operations fail"""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class PDFFileNotFoundError(PDFToolError):
    """Raised when PDF file is not found"""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class PDFPermissionError(PDFToolError):
    """Raised when PDF file permissions are insufficient"""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)
