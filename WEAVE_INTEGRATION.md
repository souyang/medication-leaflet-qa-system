# W&B Weave Integration Guide

## Overview

This project now integrates [W&B Weave](https://wandb.ai/site/weave) for comprehensive LLM application tracing and monitoring. Weave automatically logs:

- **Every RAG call**: Input query, drug parameter, output answer
- **Latency tracking**: End-to-end and per-node execution times
- **Token usage**: OpenAI API token consumption
- **Pipeline traces**: Full LangGraph node execution (route→retrieve→answer→verify→finalize)
- **Dataset logging**: Automatic logging of query/answer pairs for each API call

## Key Benefits

### 1. **Automatic Tracing**
Unlike traditional W&B experiments that require manual logging, Weave automatically captures:
- Function inputs and outputs
- Execution time
- Call hierarchy
- Model parameters

### 2. **LLM-Specific Features**
- Token usage tracking
- Cost estimation
- Prompt/completion logging
- Model version tracking

### 3. **Dataset Building**
Every production query is automatically logged, creating a dataset for:
- Model evaluation
- Regression testing
- Fine-tuning
- Quality monitoring

## Architecture

### Traced Components

```python
# RAGAgent with Weave tracing
class RAGAgent(weave.Model):
    @weave.op()
    async def query(self, query: str, drug: str | None = None, top_k: int = 6) -> QueryResponse:
        # Main entry point - logs full query execution
        pass

    @weave.op()
    def _route_intent(self, state: RAGState) -> RAGState:
        # Logs intent extraction (LLM call)
        pass

    @weave.op()
    def _retrieve(self, state: RAGState) -> RAGState:
        # Logs Redis vector search
        pass

    @weave.op()
    def _answer(self, state: RAGState) -> RAGState:
        # Logs answer generation (LLM call)
        pass

    @weave.op()
    def _verify(self, state: RAGState) -> RAGState:
        # Logs citation verification
        pass

    @weave.op()
    def _finalize(self, state: RAGState) -> RAGState:
        # Logs disclaimer addition
        pass
```

### What Gets Logged

For each `/ask` endpoint call, Weave logs:

```json
{
  "query": "What is the recommended dose of metformin?",
  "drug": "metformin",
  "top_k": 6,
  "answer": "The starting dose is 500 mg twice daily...",
  "confidence": 0.9,
  "contexts": [...],
  "latency_ms": 1240,
  "route_intent": {
    "input": {...},
    "output": {"drug": "metformin", "sections": [...]},
    "latency_ms": 450
  },
  "retrieve": {
    "input": {...},
    "output": {"contexts": [...]},
    "latency_ms": 85
  },
  "answer": {
    "input": {...},
    "output": {"draft": "..."},
    "latency_ms": 620,
    "tokens": {"prompt": 1250, "completion": 180}
  },
  "verify": {...},
  "finalize": {...}
}
```

## Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# Required for Weave
WANDB_API_KEY=your_wandb_api_key_here

# Optional configuration
WEAVE_ENABLED=true
WEAVE_PROJECT=rag-health-weave
```

### 2. Install Dependencies

```bash
# Already included in pyproject.toml
uv sync
```

### 3. Initialize Weave

Weave is automatically initialized in `apps/api/app/api.py` on FastAPI startup:

```python
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.weave_enabled and settings.wandb_api_key:
        weave.init(project_name=settings.weave_project)
        logger.info(f"✓ Weave initialized: {settings.weave_project}")
```

## Usage

### Viewing Traces

1. **Start your API**:
   ```bash
   just run-api
   ```

2. **Make a query**:
   ```bash
   curl -X POST https://medication-leaflet-qa-system.onrender.com/ask \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the recommended dose of metformin?",
       "drug": "metformin",
       "top_k": 6
     }'
   ```

3. **View in W&B UI**:
   - Go to https://wandb.ai/your-entity/rag-health-weave
   - Click on "Traces" tab
   - Select any trace to see full execution details

### Analyzing Performance

Weave provides built-in analytics:

- **Latency trends**: P50, P95, P99 over time
- **Token usage**: Cost estimation per query
- **Error rates**: Failed queries and reasons
- **Context retrieval**: Number of contexts per query

### Building Evaluation Datasets

Weave automatically creates datasets from production queries:

```python
import weave

# Load production queries
dataset = weave.ref("rag-health-weave/production-queries").get()

# Filter high-quality examples
quality_queries = [
    q for q in dataset
    if q["confidence"] > 0.9 and q["has_citation"]
]

# Use for evaluation
for query in quality_queries:
    # Run regression tests
    pass
```

## Configuration Options

### Enable/Disable Weave

```bash
# Disable tracing (useful for local development)
WEAVE_ENABLED=false
```

### Custom Project Name

```bash
# Use different project name
WEAVE_PROJECT=my-custom-project
```

### Production vs Development

```bash
# Production
WEAVE_PROJECT=rag-health-prod

# Staging
WEAVE_PROJECT=rag-health-staging

# Development
WEAVE_ENABLED=false  # Disable for local dev
```

## Integration with Existing W&B Evals

This project uses **both** W&B tools:

### 1. **W&B Experiments** (`apps/evals/`)
- **Purpose**: Batch evaluation of test dataset
- **What it logs**: Aggregate metrics (grounding rate, citation rate, latency)
- **When to use**: CI/CD regression testing, periodic quality checks

### 2. **W&B Weave** (new)
- **Purpose**: Production query tracing
- **What it logs**: Individual query traces, datasets
- **When to use**: Debugging, monitoring, dataset creation

### Workflow

```
┌─────────────────┐
│  Production     │
│  Queries (/ask) │
└────────┬────────┘
         │
         ├──> Weave Traces (individual queries)
         │
         └──> Build Dataset
                  │
                  v
         ┌────────────────┐
         │ W&B Evaluation │
         │ (batch testing)│
         └────────────────┘
```

## Performance Impact

Weave is designed for production use:

- **Minimal overhead**: ~5-10ms per query
- **Async logging**: Non-blocking
- **Configurable sampling**: Can sample 10% of queries if needed

## Best Practices

### 1. **Use Different Projects for Environments**

```python
# config.py
class Settings(BaseSettings):
    weave_project: str = "rag-health-prod"  # Change per environment
```

### 2. **Add Custom Metadata**

```python
@weave.op()
async def query(self, query: str, drug: str | None = None, top_k: int = 6) -> QueryResponse:
    # Weave automatically logs inputs/outputs
    result = await self._execute_pipeline(query, drug, top_k)

    # Add custom metadata
    weave.log({
        "user_id": request.user_id,  # If you have auth
        "deployment": "render-production",
        "redis_latency_ms": self.redis_client.last_latency
    })

    return result
```

### 3. **Monitor Key Metrics**

Create W&B dashboards to track:
- Average latency per drug
- Token usage trends
- Error rates by query type
- Context retrieval effectiveness

## Troubleshooting

### Weave Not Logging

```bash
# Check if API key is set
echo $WANDB_API_KEY

# Check logs for initialization message
tail -f logs/api.log | grep Weave
```

### High Latency

Weave logging is async, but if you experience issues:

```python
# Disable temporarily
WEAVE_ENABLED=false
```

### Token Limits

Weave logs full prompts/completions. If hitting rate limits:

```python
# Sample queries (log 10% of calls)
if random.random() < 0.1:
    weave.log({...})
```

## Next Steps

1. **Set up W&B account**: https://wandb.ai/signup
2. **Add API key** to Render environment variables
3. **Deploy** and make queries
4. **Explore traces** at https://wandb.ai/your-entity/rag-health-weave
5. **Create dashboards** for monitoring
6. **Export datasets** for evaluation

## Resources

- [W&B Weave Documentation](https://wandb.me/weave)
- [Weave Python SDK](https://github.com/wandb/weave)
- [LLM Observability Guide](https://wandb.ai/site/solutions/llm-observability)
- [Project GitHub](https://github.com/souyang/medication-leaflet-qa-system)

## Support

Questions? Reach out:
- GitHub Issues: https://github.com/souyang/medication-leaflet-qa-system/issues
- LinkedIn: https://www.linkedin.com/in/xi-ouyang
- Email: simonouyang@gmail.com

