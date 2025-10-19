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

# Start web frontend
dev-web:
    pnpm --filter web dev

# Start both API and web
dev:
    @echo "Starting full stack development..."
    @echo "API: http://localhost:8000"
    @echo "Web: http://localhost:3001"
    @echo "Press Ctrl+C to stop all services"
    #!/usr/bin/env bash
    trap 'kill %1 %2' SIGINT
    just dev-api &
    just dev-web &
    wait

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

# Format code
fmt:
    uv run ruff format .

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
    pnpm install
    just install-hooks
    just dev-redis
    @echo "Waiting for Redis..."
    sleep 3
    just seed
    @echo "✓ Setup complete. Run 'just dev' to start both API and web frontend."

# Health check
health:
    curl -s http://localhost:8000/health | jq

# Stats
stats:
    curl -s http://localhost:8000/stats | jq

# Full stack up (Docker)
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
