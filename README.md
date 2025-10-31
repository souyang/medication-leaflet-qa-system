# Medication Leaflet QA System

Production-ready RAG system for healthcare drug-label Q&A using FDA SPL data, Redis Stack, and W&B evaluation suite.

## Architecture

```
[DailyMed SPL XML] → [Parser] → [Chunker] → [Embeddings]
                                    ↓
                         [Redis Stack HNSW Index]
                                    ↓
         [LangGraph Agent: route→retrieve→answer→verify→finalize]
                                    ↓
                         [FastAPI] ← [W&B Evals]
```

## Key Features

- **Grounded answers only**: Every claim includes citation: `[Section: <name>] (<url>#section=<id>)`
- **LangGraph agent**: Multi-node verification pipeline with confidence checks
- **Redis Stack**: HNSW vector search with metadata filtering (drug, section, version)
- **W&B observability**: Weave for LLM tracing + evaluation suite with regression gates
- **Monorepo structure**: Ready for future crawlers and API expansion

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- [just](https://github.com/casey/just) (task runner)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- OpenAI API key
- W&B API key

### Setup

```bash
# 1. Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone <repo>
cd Medication-Leaflet-QA-System

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Full setup (Redis + seed data)
just setup
```

This will:
- Install all Python dependencies via uv workspace
- Start Redis Stack in Docker
- Create the search index
- Ingest 5 default drugs (metformin, lisinopril, atorvastatin, levothyroxine, amlodipine)

### Usage

```bash
# Start API server
just dev

# Command line usage:
just ask Q="What is the starting dose?" DRUG="metformin"
just ingest DRUG="aspirin"
just eval

# Deploy to production
just deploy     # Deploy using available methods

# Check health
just health

# View stats
just stats
```

### Example Query

**Request:**
```json
{
  "query": "What are the contraindications for metformin?",
  "drug": "metformin",
  "top_k": 6
}
```

**Response:**
```json
{
  "answer": "Metformin is contraindicated in:\n- Severe renal impairment (eGFR <30) [Section: CONTRAINDICATIONS] (https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=xxx#section=34070-3)\n- Metabolic acidosis...\n\n⚠️ Not medical advice. Verify via linked label.",
  "confidence": 0.9,
  "contexts": [...],
  "drug": "metformin",
  "disclaimer": "Not medical advice. Verify via linked label."
}
```

## Project Structure

```
medication-leaflet-qa-system/
├── apps/
│   ├── api/              # FastAPI + LangGraph agent
│   │   ├── app/
│   │   │   ├── api.py    # FastAPI endpoints
│   │   │   ├── agent.py  # LangGraph RAG agent
│   │   │   └── ingest.py # SPL parsing & ingestion
│   │   └── scripts/
│   │       └── seed_ingest.py
│   └── evals/            # W&B evaluation suite
│       └── app/
│           └── evals.py
├── packages/
│   └── py/
│       ├── core/         # Shared types, prompts, config
│       │   └── rag_health_core/
│       │       ├── types.py
│       │       ├── prompts.py
│       │       └── config.py
│       └── retrieval/    # Redis + embeddings
│           └── rag_health_retrieval/
│               ├── redis_client.py
│               ├── embeddings.py
│               └── chunker.py
├── infra/
│   ├── docker-compose.yml
│   └── Dockerfile
├── Justfile              # Task runner
└── pyproject.toml        # uv workspace root
```

## API Endpoints

- `GET /health` - Health check (Redis connectivity)
- `POST /ask` - Query drug labels
- `POST /ingest/{drug_name}` - Ingest new drug
- `POST /index/create?drop_existing=false` - Create/recreate index
- `GET /stats` - Document count

## LangGraph Flow

1. **route_intent**: Extract drug + target sections via LLM
2. **retrieve**: Redis KNN search with filters
3. **answer**: Generate response from contexts
4. **verify**: Check citations + confidence threshold
5. **finalize**: Add disclaimer

## Redis Schema

**Key pattern:** `doc:{setid}:{section}:{version}:{hash}`

**Fields:**
- `drug_name` (TAG): filterable drug name
- `section` (TAG): section code (e.g., `DOSAGE_AND_ADMINISTRATION`)
- `version` (NUMERIC): version counter
- `text` (TEXT): chunk content
- `emb` (VECTOR): HNSW embedding (3072-dim)

## Observability & Evaluation

### W&B Weave (LLM Tracing)
Automatic tracing of every production query:
- Full LangGraph pipeline traces
- Token usage and cost tracking
- Latency per node
- Dataset building from production queries

See [WEAVE_INTEGRATION.md](WEAVE_INTEGRATION.md) for setup.

### W&B Evaluation Suite
Run `just eval` to measure:
- **Grounding rate**: % of answers with valid context
- **Citation rate**: % of answers with proper citations
- **Latency**: p50/p95 response times
- **Hallucination**: manual spot checks (future: auto detection)

Results logged to W&B with regression gates.

## Development Tasks

```bash
just lint          # Ruff linting
just fmt           # Format code
just typecheck     # mypy type checking
just test          # pytest
just clean         # Remove cache/artifacts
```

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `REDIS_URL` | redis://localhost:6379 | Redis connection URL |
| `REDIS_HOST` | localhost | Redis host (fallback) |
| `REDIS_PORT` | 6379 | Redis port (fallback) |
| `REDIS_PASSWORD` | None | Redis password (fallback) |
| `CHUNK_SIZE` | 1536 | Tokens per chunk |
| `CHUNK_OVERLAP` | 150 | Overlap tokens |
| `RETRIEVAL_TOP_K` | 6 | Max contexts per query |
| `WANDB_PROJECT` | rag-health-poc | W&B project name |
| `WANDB_ENTITY` | None | W&B entity/team name |

## Compliance & Safety

- **Data source**: Public FDA SPL labels via DailyMed API
- **No PHI**: System processes only publicly available drug labels
- **Disclaimers**: All answers include "Not medical advice" disclaimer
- **Citations**: Every claim linked to source section
- **Robots.txt**: Respects DailyMed rate limits and ToS

## Future Roadmap

- [ ] Advanced hallucination detection
- [ ] Multi-drug interaction queries
- [ ] Real-time drug label updates
- [ ] Enhanced evaluation metrics

## License

MIT

## Contributing

This is a production-ready healthcare RAG system. Contributions are welcome for:
- Enhanced evaluation metrics
- Additional drug data sources
- Performance optimizations
- Documentation improvements

## Support

For technical questions or issues, please open a GitHub issue or connect on LinkedIn.
