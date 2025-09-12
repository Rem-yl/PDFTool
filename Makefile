# PDFTool Makefile

.PHONY: help install install-dev test test-cov lint format clean build run-gui run-api docker-build docker-run

# Default target
help:
	@echo "PDFTool Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install package and dependencies"
	@echo "  install-dev Install package with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black"
	@echo "  clean       Clean build artifacts"
	@echo ""
	@echo "Build:"
	@echo "  build       Build package distributions"
	@echo ""
	@echo "Run:"
	@echo "  run-gui     Start GUI application"
	@echo "  run-api     Start API server"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,api]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/pdftool --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/pdftool tests/
	mypy src/pdftool
	black --check src/pdftool tests/

format:
	black src/pdftool tests/
	isort src/pdftool tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	python -m build

# Run applications
run-gui:
	python -m pdftool.gui.main

run-api:
	python -m pdftool.api.main

run-api-dev:
	uvicorn pdftool.api.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-build:
	docker build -t pdftool:latest .

docker-run:
	docker run -p 8000:8000 pdftool:latest

# Development server with hot reload
dev-api:
	PDFTOOL_DEBUG=true uvicorn pdftool.api.main:app --reload --host 0.0.0.0 --port 8000

# Check dependencies for security vulnerabilities
security-check:
	pip-audit

# Generate requirements.txt from pyproject.toml
requirements:
	pip-compile pyproject.toml