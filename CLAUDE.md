# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDFTool is a comprehensive PDF manipulation tool with three interfaces:
- **GUI Desktop Application**: Tkinter-based desktop app with drag-and-drop support
- **Web API**: FastAPI-based REST API with Web UI 
- **CLI**: Command-line interface for PDF operations

Core operations: PDF merge, split, info extraction, with planned features including compression, watermarking, password protection, and format conversion.

## Development Commands

### Setup and Installation
```bash
# Install package with all dependencies
make install-dev

# Install package only
make install
```

### Running Applications
```bash
# Start GUI application
make run-gui
# Alternative: python -m pdftool.gui.main

# Start API server (production)
make run-api
# Alternative: python -m pdftool.api.main

# Start API server with hot reload (development)
make dev-api
# Alternative: uvicorn pdftool.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing and Code Quality
```bash
# Run all tests
make test
# Alternative: pytest tests/ -v

# Run tests with coverage
make test-cov
# Alternative: pytest tests/ -v --cov=src/pdftool --cov-report=html --cov-report=term

# Code linting and type checking
make lint
# Runs: flake8, mypy, black --check

# Code formatting
make format
# Runs: black, isort
```

### Docker Operations
```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Full Docker Compose deployment
docker-compose up --build
```

### Build and Cleanup
```bash
# Build package distributions
make build

# Clean build artifacts
make clean
```

## Architecture Overview

### Package Structure
```
src/pdftool/
├── core/              # Core business logic
│   ├── pdf_operations.py   # Main PDF processing class
│   ├── models.py           # Pydantic data models (PDFInfo, SplitOptions, etc.)
│   └── exceptions.py       # Custom exception classes
├── api/               # FastAPI web interface
│   ├── main.py            # FastAPI app with endpoints (/merge, /split, /info)
│   └── templates.py       # HTML template generation
├── gui/               # Desktop GUI application
│   └── main.py            # Tkinter-based GUI with tabbed interface
├── config/            # Configuration management
│   └── settings.py        # Pydantic BaseSettings with env var support
└── utils/             # Utility modules
    ├── logging.py         # Structured logging setup
    └── validators.py      # Input validation utilities
```

### Key Design Patterns

**Core Engine**: `PDFOperations` class in `core/pdf_operations.py` handles all PDF processing using PyPDF2. All interfaces (GUI, API, CLI) delegate to this core class.

**Configuration**: Environment-based configuration through `config/settings.py` using Pydantic BaseSettings. Supports `.env` files and environment variables prefixed with `PDFTOOL_`.

**Error Handling**: Hierarchical custom exceptions in `core/exceptions.py`:
- `PDFToolError` (base)
- `PDFValidationError`, `PDFProcessingError`, `PDFFileNotFoundError`

**Data Models**: Pydantic models in `core/models.py` for type safety:
- `PDFInfo`: File metadata and properties
- `SplitOptions`/`MergeOptions`: Operation configuration
- `OperationResult`: Standardized response format

### API Endpoints

- `GET /`: Web interface HTML
- `POST /merge`: Merge multiple PDFs
- `POST /split`: Split PDF (modes: all pages, page range)
- `POST /info`: Extract PDF metadata
- `GET /health`: Health check endpoint

### Entry Points

The package defines console scripts in `pyproject.toml`:
- `pdftool-gui`: Launches desktop application
- `pdftool-api`: Starts API server

## Environment Configuration

Key environment variables (all prefixed with `PDFTOOL_`):
- `PDFTOOL_DEBUG`: Enable debug mode
- `PDFTOOL_TEMP_DIR`: Temporary file directory (default: "temp")
- `PDFTOOL_MAX_FILE_SIZE`: Max upload size in bytes (default: 100MB)
- `PDFTOOL_API_HOST`/`PDFTOOL_API_PORT`: API server binding
- `PDFTOOL_LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Testing

Tests are located in `tests/` directory using pytest. Key test configurations in `pyproject.toml`:
- Coverage reporting with `--cov=src/pdftool`
- HTML coverage reports generated in `htmlcov/`
- Test discovery pattern: `test_*.py` files

## Dependencies

Core dependencies (see `requirements.txt`):
- `PyPDF2>=3.0.0`: PDF processing engine
- `fastapi>=0.104.0`: Web framework
- `uvicorn>=0.24.0`: ASGI server
- `python-multipart>=0.0.6`: File upload support

Development dependencies include pytest, black, flake8, mypy, and pre-commit hooks.

## Code Quality Standards

- **Formatting**: Black with 100-character line length
- **Type Checking**: mypy with strict configuration
- **Linting**: flake8 for code quality
- **Testing**: pytest with coverage requirements
- **Pre-commit**: Automated quality checks on commit