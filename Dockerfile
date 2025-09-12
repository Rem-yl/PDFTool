# Multi-stage Dockerfile for PDFTool API

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py ./

# Install the package
RUN pip install -e .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r pdftool && useradd -r -g pdftool pdftool

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Create necessary directories
RUN mkdir -p /app/temp /app/logs
RUN chown -R pdftool:pdftool /app

# Switch to non-root user
USER pdftool

# Environment variables
ENV PYTHONPATH=/app/src
ENV PDFTOOL_TEMP_DIR=/app/temp
ENV PDFTOOL_LOG_FILE=/app/logs/pdftool.log

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "pdftool.api.main:app", "--host", "0.0.0.0", "--port", "8000"]