# Dockerfile per Railway - Karaokati Backend
FROM python:3.11-slim

# Environment variables per ottimizzazioni Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create static directory for FastAPI static files (if needed)
RUN mkdir -p static

# Create non-root user (Railway friendly)
RUN adduser --disabled-password --gecos '' --shell /bin/sh appuser \
    && chown -R appuser:appuser /app
USER appuser

# Health check (usando $PORT dynamica)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 🚀 Start application (Railway fornisce $PORT automaticamente)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT