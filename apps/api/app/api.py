"""FastAPI application with RAG endpoints."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from rag_health_core import QueryRequest, QueryResponse, Settings

from app.agent import RAGAgent
from app.ingest import IngestionService

settings = Settings()
rag_agent: RAGAgent | None = None
ingest_service: IngestionService | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize services on startup."""
    global rag_agent, ingest_service
    rag_agent = RAGAgent(settings)
    ingest_service = IngestionService(settings)
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    redis_ok = rag_agent.redis_client.ping()

    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
    }


@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest) -> QueryResponse:
    """Ask a question about drug labels."""
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    try:
        return await rag_agent.query(
            query=request.query,
            drug=request.drug,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Query failed: {e}") from e


@app.post("/ingest/{drug_name}")
async def ingest(drug_name: str) -> dict[str, int | str]:
    """Ingest drug label from DailyMed."""
    if ingest_service is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Ingest service not initialized")

    try:
        count = await ingest_service.ingest_drug(drug_name)
        return {
            "drug": drug_name,
            "chunks_ingested": count,
        }
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Ingestion failed: {e}") from e


@app.post("/index/create")
async def create_index(drop_existing: bool = False) -> dict[str, str]:
    """Create or recreate the Redis search index."""
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    try:
        rag_agent.redis_client.create_index(drop_existing=drop_existing)
        return {"status": "created", "index": settings.redis_index_name}
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, f"Index creation failed: {e}"
        ) from e


@app.get("/stats")
async def stats() -> dict[str, int]:
    """Get index statistics."""
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    count = rag_agent.redis_client.count_documents()
    return {"document_count": count}
