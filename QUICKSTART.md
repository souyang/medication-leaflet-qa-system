# Quick Start Guide

Get the RAG Health POC running in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker
- OpenAI API key

## Installation

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install just (task runner) - macOS
brew install just
# Or see: https://github.com/casey/just#installation

# 3. Clone repository
cd Medication-Leaflet-QA-System
```

## Configuration

```bash
# Create .env file
cp env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-...
```

## Setup & Run

```bash
# One-command setup (installs deps, starts Redis, seeds data)
just setup

# In a new terminal, start the API
just dev-api

# API now running at http://localhost:8000
```

## First Query

```bash
# Ask a question
just ask Q="What is the recommended starting dose?" DRUG="metformin"

# Or use curl directly
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the contraindications?", "drug": "metformin"}'
```

## What Just Happened?

1. **`just setup`** executed:
   - Installed Python packages via uv workspace
   - Started Redis Stack in Docker (port 6379 + RedisInsight on 8001)
   - Created HNSW vector search index
   - Ingested 5 default drugs from DailyMed (metformin, lisinopril, atorvastatin, levothyroxine, amlodipine)
   - Parsed SPL XML → chunked → embedded → indexed

2. **`just dev-api`** started FastAPI with hot reload

3. **`just ask`** sent POST to `/ask` endpoint → LangGraph agent:
   - Routed query to target sections
   - Retrieved top-6 relevant chunks via Redis KNN
   - Generated answer with LLM
   - Verified citations present
   - Added disclaimer

## Next Steps

```bash
# Ingest a new drug
just ingest DRUG="ibuprofen"

# Check system health
just health

# View statistics
just stats

# Run evaluations (requires W&B)
just eval

# Open RedisInsight (GUI)
open http://localhost:8001
```

## Verify Installation

```bash
# Check all components
curl http://localhost:8000/health
# Expected: {"status": "healthy", "redis": "connected"}

curl http://localhost:8000/stats
# Expected: {"document_count": 50}  (approx., depends on drugs seeded)
```

## Troubleshooting

**Redis connection failed:**
```bash
just dev-redis  # Ensure Redis is running
docker ps       # Check container status
```

**Import errors:**
```bash
uv sync  # Re-sync dependencies
```

**No documents found:**
```bash
just seed  # Re-run seed script
```

**OpenAI API errors:**
- Check `.env` has valid `OPENAI_API_KEY`
- Verify API quota/rate limits

## Architecture Diagram

```
┌─────────────────┐
│   DailyMed API  │ (SPL XML source)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ingest Service │ (Parse, chunk, embed)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redis Stack    │ (HNSW index + JSON docs)
│  localhost:6379 │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  LangGraph RAG Agent                │
│  route → retrieve → answer → verify │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │
│  localhost:8000 │
└─────────────────┘
```

## Key Files

- `apps/api/app/api.py` - FastAPI endpoints
- `apps/api/app/agent.py` - LangGraph agent logic
- `apps/api/app/ingest.py` - SPL parsing & ingestion
- `packages/py/core/rag_health_core/types.py` - Core data models
- `packages/py/retrieval/rag_health_retrieval/redis_client.py` - Redis operations
- `Justfile` - Task definitions

## Development Tasks

```bash
just lint       # Lint with ruff
just fmt        # Format code
just typecheck  # Type check with mypy
just test       # Run pytest
```

## Ready to Extend?

See [README.md](README.md) for full documentation and [DECISIONS.md](DECISIONS.md) for architectural rationale.
