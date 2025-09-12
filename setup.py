"""
Setup script for PDFTool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = requirements_file.read_text().strip().split('\n') if requirements_file.exists() else []

setup(
    name="pdftool",
    version="1.0.0",
    author="PDFTool Team",
    author_email="contact@pdftool.com",
    description="A comprehensive PDF manipulation tool with GUI and API interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pdftool/pdftool",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "api": [
            "pydantic>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdftool-gui=pdftool.gui.main:main",
            "pdftool-api=pdftool.api.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)