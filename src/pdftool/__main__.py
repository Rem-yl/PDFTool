"""
PDFTool package main entry point

Provides the main entry point when the package is executed as:
python -m pdftool

Directly starts the Web service for PDF operations.
"""

from .interfaces.web.main import main

if __name__ == "__main__":
    main()
