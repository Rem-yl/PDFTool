# Migration Guide

This document helps you migrate from the old PDFTool structure to the new engineered architecture.

## What Changed

### Directory Structure

**Old Structure:**
```
pdftool/
├── main.py          # FastAPI web interface
├── pdf_tool.py      # GUI application
├── requirements.txt
├── README.md
└── temp/           # Temporary files
```

**New Structure:**
```
pdftool/
├── src/
│   └── pdftool/
│       ├── __init__.py
│       ├── core/           # Core business logic
│       │   ├── pdf_operations.py
│       │   ├── models.py
│       │   └── exceptions.py
│       ├── api/            # FastAPI web interface
│       │   ├── main.py
│       │   └── templates.py
│       ├── gui/            # Modern GUI interface
│       │   └── main.py
│       ├── config/         # Configuration management
│       │   └── settings.py
│       └── utils/          # Utilities
│           ├── logging.py
│           └── validators.py
├── tests/              # Test suite
├── docs/               # Documentation
├── scripts/            # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── setup.py
```

## Breaking Changes

### 1. Import Changes

**Old:**
```python
# These files no longer exist at root level
from main import app
from pdf_tool import PDFTool
```

**New:**
```python
# Use proper package imports
from pdftool.api.main import app
from pdftool.gui.main import ModernPDFTool
from pdftool.core.pdf_operations import PDFOperations
```

### 2. Configuration

**Old:**
```python
# Hardcoded settings in files
TEMP_DIR = Path("temp")
```

**New:**
```python
# Centralized configuration
from pdftool.config.settings import settings
temp_dir = settings.temp_dir
```

### 3. Error Handling

**Old:**
```python
# Generic exceptions
try:
    # PDF operation
except Exception as e:
    print(f"Error: {e}")
```

**New:**
```python
# Specific exception types
from pdftool.core.exceptions import PDFValidationError, PDFProcessingError

try:
    # PDF operation
except PDFValidationError as e:
    # Handle validation errors
except PDFProcessingError as e:
    # Handle processing errors
```

## Migration Steps

### 1. Update Dependencies

Install the new package:
```bash
pip install -e .
# Or with development dependencies
pip install -e ".[dev,api]"
```

### 2. Update Code

Replace direct file imports with package imports:

```python
# OLD
from main import merge_pdfs
from pdf_tool import PDFMergeWindow

# NEW
from pdftool.core.pdf_operations import PDFOperations
from pdftool.gui.main import ModernPDFTool
```

### 3. Update Configuration

Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Update Scripts

**Old script:**
```bash
python main.py
```

**New commands:**
```bash
# API server
pdftool-api
# or
python -m pdftool.api.main

# GUI application
pdftool-gui
# or
python -m pdftool.gui.main
```

## New Features

### 1. Type Safety
All modules now include proper type hints for better IDE support and error detection.

### 2. Configuration Management
Environment-based configuration with `.env` file support.

### 3. Proper Logging
Structured logging with configurable levels and file output.

### 4. Error Handling
Specific exception types for different error conditions.

### 5. Testing
Comprehensive test suite with pytest.

### 6. Docker Support
Containerized deployment with Docker and docker-compose.

### 7. Development Tools
- Makefile for common tasks
- Pre-commit hooks
- Code formatting with black
- Linting with flake8
- Type checking with mypy

## API Changes

### Core API

**Old:**
```python
# Direct PyPDF2 usage
import PyPDF2
merger = PyPDF2.PdfMerger()
# ... manual error handling
```

**New:**
```python
# High-level operations API
from pdftool.core.pdf_operations import PDFOperations
from pdftool.core.models import MergeOptions

pdf_ops = PDFOperations()
options = MergeOptions(output_file=Path("merged.pdf"))
result = pdf_ops.merge_pdfs(input_files, options)
```

### Web API

The FastAPI endpoints remain the same, but now use the core operations module for better consistency and error handling.

### GUI API

The GUI has been modernized with better UX and proper separation of concerns.

## Compatibility Notes

- Python 3.8+ required
- All original functionality preserved
- Performance improvements
- Better error messages
- Enhanced logging

## Getting Help

If you encounter issues during migration:

1. Check the logs in `logs/pdftool.log`
2. Review the test suite for usage examples
3. Check the API documentation at `/docs` when running the API server
4. Refer to the comprehensive README.md

## Rollback Plan

If you need to rollback to the old structure temporarily:

1. Keep a backup of your old files
2. The old `main.py` and `pdf_tool.py` files are preserved for reference
3. Revert to the old requirements.txt if needed

However, we recommend migrating to the new structure for better maintainability and future updates.