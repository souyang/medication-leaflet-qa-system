FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy workspace files
COPY pyproject.toml .
COPY packages/ packages/
COPY apps/api/ apps/api/

# Install dependencies
RUN uv pip install --system -e apps/api

# Expose API port
EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
