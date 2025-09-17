"""
Validation utilities for file operations
"""

import mimetypes
from pathlib import Path
from typing import List

from ..config.settings import settings
from ..core.exceptions import PDFValidationError


def validate_file_size(file_path: Path) -> None:
    """Validate that file size is within limits"""
    file_size = file_path.stat().st_size
    if file_size > settings.max_file_size:
        raise PDFValidationError(
            f"File size ({file_size} bytes) exceeds maximum allowed size "
            f"({settings.max_file_size} bytes)"
        )


def validate_file_extension(file_path: Path) -> None:
    """Validate that file has allowed extension"""
    if file_path.suffix.lower() not in settings.allowed_extensions:
        raise PDFValidationError(
            f"File extension '{file_path.suffix}' is not allowed. "
            f"Allowed extensions: {', '.join(settings.allowed_extensions)}"
        )


def validate_mime_type(file_path: Path) -> None:
    """Validate file MIME type"""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type != "application/pdf":
        raise PDFValidationError(f"Invalid MIME type: {mime_type}. Expected: application/pdf")


def validate_pdf_files(file_paths: List[Path]) -> None:
    """Validate multiple PDF files"""
    for file_path in file_paths:
        if not file_path.exists():
            raise PDFValidationError(f"File not found: {file_path}")

        validate_file_size(file_path)
        validate_file_extension(file_path)
        validate_mime_type(file_path)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Limit filename length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name_length = 250 - len(ext)
        filename = name[:max_name_length] + ("." + ext if ext else "")

    return filename
