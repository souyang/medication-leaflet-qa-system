# Justfile for RAG Health monorepo

# Default recipe
default:
    @just --list

# Start Redis in background
dev-redis:
    docker compose -f infra/docker-compose.yml up redis -d

# Stop Redis
stop-redis:
    docker compose -f infra/docker-compose.yml down

# Start API server
dev-api:
    cd apps/api && PYTHONPATH=. uv run uvicorn app.api:app --reload --port 8000

# Start API server (development)
dev:
    @echo "Starting API development server..."
    @echo "API: http://localhost:8000"
    @echo "Press Ctrl+C to stop the service"
    just dev-api

# Create Redis index
create-index DROP="false":
    uv run --project apps/api python -c "from app.api import settings; from rag_health_retrieval import RedisClient; RedisClient(settings).create_index(drop_existing={{DROP}}=='true')"

# Ingest drug label
ingest DRUG="metformin":
    cd apps/api && PYTHONPATH=. uv run python scripts/seed_ingest.py --drug {{DRUG}}

# Ingest default drugs with index creation
seed:
    cd apps/api && PYTHONPATH=. uv run python scripts/seed_ingest.py --create-index --drop-existing

# Ask a question
ask Q="What is the recommended dose?" DRUG="metformin":
    #!/usr/bin/env bash
    curl -s http://localhost:8000/ask -X POST \
      -H 'Content-Type: application/json' \
      -d '{"query":"{{Q}}","drug":"{{DRUG}}"}' | jq

# Run evaluations
eval:
    uv run --project apps/evals python apps/evals/app/evals.py

# Lint all code
lint:
    uv run ruff check .

# Lint with auto-fix
lint-fix:
    uv run ruff check --fix .

# Lint with auto-fix (including unsafe fixes)
lint-fix-unsafe:
    uv run ruff check --fix --unsafe-fixes .

# Format code
fmt:
    uv run ruff format .

# Format and fix all issues
fix-all:
    uv run ruff format .
    uv run ruff check --fix --unsafe-fixes .

# Type check
typecheck:
    uv run mypy packages/py apps/api apps/evals

# Run tests
test:
    uv run pytest

# Install pre-commit hooks
install-hooks:
    uv run pre-commit install

# Full dev setup
setup:
    @echo "Setting up RAG Health development environment..."
    uv sync
    just install-hooks
    just dev-redis
    @echo "Waiting for Redis..."
    sleep 3
    just seed
    @echo "✓ Setup complete. Run 'just dev' to start the API server."

# Health check
health:
    curl -s http://localhost:8000/health | jq

# Stats
stats:
    curl -s http://localhost:8000/stats | jq

# Backend only (Docker)
up:
    docker compose -f infra/docker-compose.yml up -d

# Full stack down
down:
    docker compose -f infra/docker-compose.yml down

# Clean all artifacts
clean:
    rm -rf .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name "*.egg-info" -exec rm -rf {} +

# Deploy to production
deploy:
    @echo "Deploying to production..."
    @echo "Use one of the deployment methods below:"
    @echo "1. Render: just deploy-render"
    @echo "2. Docker: just deploy-docker"

# Deploy to Render (recommended alternative)
deploy-render:
    @echo "Deploying to Render..."
    @echo "1. Go to render.com and sign up with GitHub"
    @echo "2. Create New Web Service"
    @echo "3. Connect your GitHub repository"
    @echo "4. Use these settings:"
    @echo "   - Build Command: pip install -r requirements.txt && pip install -e packages/py/core && pip install -e packages/py/retrieval && pip install -e apps/api"
    @echo "   - Start Command: cd apps/api && uvicorn app.api:app --host 0.0.0.0 --port $PORT"
    @echo "   - Environment: Python 3.11"
    @echo "5. Set environment variables: OPENAI_API_KEY, WANDB_API_KEY, WANDB_ENTITY"

# Deploy with Docker (works on any platform)
deploy-docker:
    @echo "Building Docker image..."
    docker build -t rag-health-api .
    @echo "Docker image built successfully!"
    @echo "You can now deploy this image to any platform that supports Docker:"
    @echo "- AWS App Runner"
    @echo "- Google Cloud Run"
    @echo "- DigitalOcean App Platform"
    @echo "- Heroku Container Registry"
