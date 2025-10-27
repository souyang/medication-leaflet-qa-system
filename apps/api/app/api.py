"""FastAPI application with RAG endpoints."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from rag_health_core import QueryRequest, QueryResponse, Settings

from app.agent import RAGAgent
from app.ingest import IngestionService

settings = Settings()
rag_agent: RAGAgent | None = None
ingest_service: IngestionService | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize services on startup."""
    global rag_agent, ingest_service
    rag_agent = RAGAgent(settings)
    ingest_service = IngestionService(settings)
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=f"""
    ## Medication Leaflet QA System API

    **Copyright © {datetime.now().year} Simon Ouyang. All rights reserved.**

    A production-ready RAG (Retrieval-Augmented Generation) system for healthcare drug-label Q&A using FDA SPL data.

    ### Key Features:
    - **Grounded answers only**: Every claim includes citation with source section and URL
    - **LangGraph agent**: Multi-node verification pipeline with confidence checks
    - **Redis Stack**: HNSW vector search with metadata filtering
    - **W&B observability**: Traces and evals with regression gates

    ### Architecture:
    ```
    [DailyMed SPL XML] → [Parser] → [Chunker] → [Embeddings]
                                        ↓
                             [Redis Stack HNSW Index]
                                        ↓
         [LangGraph Agent: route→retrieve→answer→verify→finalize]
                                        ↓
                             [FastAPI] ← [W&B Evals]
    ```

    ### Compliance & Safety:
    - **Data source**: Public FDA SPL labels via DailyMed API
    - **No PHI**: System processes only publicly available drug labels
    - **Disclaimers**: All answers include "Not medical advice" disclaimer
    - **Citations**: Every claim linked to source section
    """,
    lifespan=lifespan,
    contact={
        "name": "Simon Ouyang",
        "url": "https://github.com/souyang/medication-leaflet-qa-system",
        "email": "simonouyang@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "https://medication-leaflet-qa-system.onrender.com",
            "description": "Production server",
        },
        {"url": "http://localhost:8000", "description": "Local development server"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the API and Redis connection. Returns the overall system status and Redis connectivity.",
    response_description="System health status",
    tags=["System"],
    responses={
        200: {
            "description": "System health status",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy": {
                            "summary": "System is healthy",
                            "value": {"status": "healthy", "redis": "connected"},
                        },
                        "degraded": {
                            "summary": "System is degraded",
                            "value": {"status": "degraded", "redis": "disconnected"},
                        },
                    }
                }
            },
        },
        503: {
            "description": "Service Unavailable",
            "content": {"application/json": {"example": {"detail": "Agent not initialized"}}},
        },
    },
)
async def health() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
    - **status**: "healthy" if all systems operational, "degraded" if Redis is down
    - **redis**: "connected" if Redis is accessible, "disconnected" if not

    Use this endpoint to monitor system health and troubleshoot connection issues.
    """
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    redis_ok = rag_agent.redis_client.ping()

    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
    }


@app.post(
    "/ask",
    response_model=QueryResponse,
    summary="Ask Drug Questions",
    description="Ask questions about drug labels and get AI-powered answers with citations. The system uses RAG (Retrieval-Augmented Generation) to provide grounded, cited responses.",
    response_description="AI-generated answer with citations and confidence score",
    tags=["Drug Queries"],
    responses={
        200: {
            "description": "Successful query response",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "The recommended starting dose for metformin is 500mg twice daily with meals, or 850mg once daily. The maximum daily dose is 2550mg. [Section: DOSAGE_AND_ADMINISTRATION] (https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=xxx#section=34070-3)",
                        "confidence": 0.92,
                        "contexts": [
                            {
                                "text": "The usual starting dose of metformin is 500mg twice daily with meals...",
                                "section": "DOSAGE_AND_ADMINISTRATION",
                                "section_id": "34070-3",
                                "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=xxx",
                                "score": 0.95,
                            }
                        ],
                        "drug": "metformin",
                        "disclaimer": "Not medical advice. Verify via linked label.",
                    }
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "query"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Query failed: Redis search failed: Error connecting to Redis"
                    }
                }
            },
        },
    },
)
async def ask(request: QueryRequest) -> QueryResponse:
    """
    Ask a question about drug labels.

    This endpoint uses a LangGraph agent to:
    1. **Route** the query to identify target sections
    2. **Retrieve** relevant chunks from Redis vector search
    3. **Answer** using LLM with retrieved context
    4. **Verify** citations and confidence
    5. **Finalize** with disclaimers

    **Example Questions:**
    - "What is the starting dose for metformin?"
    - "What are the side effects of lisinopril?"
    - "What are the contraindications for atorvastatin?"
    - "What are the drug interactions with aspirin?"

    **Response includes:**
    - **answer**: AI-generated response with citations
    - **confidence**: Confidence score (0.0-1.0)
    - **contexts**: Retrieved source chunks with citations
    - **drug**: Drug name if specified
    - **disclaimer**: Medical advice disclaimer
    """
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


@app.post(
    "/ingest/{drug_name}",
    summary="Ingest Drug Data",
    description="Ingest drug label data from DailyMed API. Parses SPL XML, chunks text, generates embeddings, and stores in Redis vector index.",
    response_description="Ingestion results with chunk count",
    tags=["Data Management"],
    responses={
        200: {
            "description": "Drug successfully ingested",
            "content": {
                "application/json": {"example": {"drug": "metformin", "chunks_ingested": 45}}
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "drug_name"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Ingestion failed: Drug not found in DailyMed"}
                }
            },
        },
    },
)
async def ingest(drug_name: str) -> dict[str, int | str]:
    """
    Ingest drug label from DailyMed.

    This endpoint:
    1. **Fetches** drug label from DailyMed API
    2. **Parses** SPL XML structure
    3. **Chunks** text into manageable pieces
    4. **Generates** embeddings using OpenAI
    5. **Stores** in Redis vector index

    **Available drugs:**
    - metformin, lisinopril, atorvastatin, levothyroxine, amlodipine
    - aspirin, ibuprofen, acetaminophen, omeprazole, simvastatin

    **Response includes:**
    - **drug**: Drug name that was ingested
    - **chunks_ingested**: Number of text chunks processed and stored
    """
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


@app.post(
    "/index/create",
    summary="Create Search Index",
    description="Create or recreate the Redis search index with HNSW vector search capabilities. Required before ingesting drugs.",
    response_description="Index creation status",
    tags=["Data Management"],
    responses={
        200: {
            "description": "Index created successfully",
            "content": {
                "application/json": {"example": {"status": "created", "index": "idx:leaflets"}}
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "drop_existing"],
                                "msg": "value is not a valid boolean",
                                "type": "type_error.bool",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Index creation failed: Redis connection error"}
                }
            },
        },
    },
)
async def create_index(drop_existing: bool = False) -> dict[str, str]:
    """
    Create or recreate the Redis search index.

    This endpoint creates a RediSearch index with:
    - **HNSW vector field** for similarity search
    - **Tag fields** for filtering (drug, section, version)
    - **Text field** for full-text search
    - **Numeric field** for version tracking

    **Parameters:**
    - **drop_existing**: If true, drops existing index and recreates from scratch

    **Use this:**
    - Before ingesting any drugs
    - If you need to reset the index
    - After Redis connection issues
    """
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    try:
        rag_agent.redis_client.create_index(drop_existing=drop_existing)
        return {"status": "created", "index": settings.redis_index_name}
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, f"Index creation failed: {e}"
        ) from e


@app.get(
    "/stats",
    summary="Get System Statistics",
    description="Get statistics about the number of documents in the Redis index. Useful for monitoring data ingestion.",
    response_description="Document count statistics",
    tags=["System"],
    responses={
        200: {
            "description": "Document count statistics",
            "content": {
                "application/json": {
                    "examples": {
                        "empty": {"summary": "No data ingested", "value": {"document_count": 0}},
                        "single_drug": {
                            "summary": "Single drug ingested",
                            "value": {"document_count": 45},
                        },
                        "multiple_drugs": {
                            "summary": "Multiple drugs ingested",
                            "value": {"document_count": 150},
                        },
                    }
                }
            },
        },
        503: {
            "description": "Service Unavailable",
            "content": {"application/json": {"example": {"detail": "Agent not initialized"}}},
        },
    },
)
async def stats() -> dict[str, int]:
    """
    Get index statistics.

    Returns the total number of document chunks stored in the Redis index.
    This helps you monitor:
    - How much data has been ingested
    - Whether ingestion was successful
    - System capacity and usage

    **Typical values:**
    - **0**: No data ingested yet
    - **50-200**: Single drug ingested
    - **500+**: Multiple drugs ingested
    """
    if rag_agent is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agent not initialized")

    count = rag_agent.redis_client.count_documents()
    return {"document_count": count}
