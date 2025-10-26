# Production Dockerfile for RAG Health API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy workspace packages
COPY packages/py/core ./packages/py/core
COPY packages/py/retrieval ./packages/py/retrieval
COPY apps/api ./apps/api

# Install workspace packages in development mode
RUN pip install -e packages/py/core
RUN pip install -e packages/py/retrieval
RUN pip install -e apps/api

# Set working directory to API
WORKDIR /app/apps/api

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
