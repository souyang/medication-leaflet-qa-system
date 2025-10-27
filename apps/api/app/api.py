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
<p><strong>Copyright © {datetime.now().year} Simon Ouyang. All rights reserved.</strong></p>

<p>
<a href="https://github.com/souyang/medication-leaflet-qa-system" target="_blank">
<img src="https://img.shields.io/github/stars/souyang/medication-leaflet-qa-system?style=social" alt="GitHub stars"/>
</a>
<a href="https://github.com/souyang/medication-leaflet-qa-system" target="_blank">⭐ Star this repository on GitHub</a>
</p>

<p>A production-ready RAG (Retrieval-Augmented Generation) system for healthcare drug-label Q&A using FDA SPL data.</p>

<h3>Key Features</h3>
<ul>
<li><strong>Grounded answers only</strong>: Every claim includes citation with source section and URL</li>
<li><strong>LangGraph agent</strong>: Multi-node verification pipeline with confidence checks</li>
<li><strong>Redis Stack</strong>: HNSW vector search with metadata filtering</li>
<li><strong>W&B observability</strong>: Traces and evals with regression gates</li>
</ul>

<h3>Architecture</h3>
<pre>
[DailyMed SPL XML] → [Parser] → [Chunker] → [Embeddings]
                                    ↓
                         [Redis Stack HNSW Index]
                                    ↓
     [LangGraph Agent: route→retrieve→answer→verify→finalize]
                                    ↓
                         [FastAPI] ← [W&B Evals]
</pre>

<h3>Compliance & Safety</h3>
<ul>
<li><strong>Data source</strong>: Public FDA SPL labels via DailyMed API</li>
<li><strong>No PHI</strong>: System processes only publicly available drug labels</li>
<li><strong>Disclaimers</strong>: All answers include "Not medical advice" disclaimer</li>
<li><strong>Citations</strong>: Every claim linked to source section</li>
</ul>
    """,
    lifespan=lifespan,
    contact={
        "name": "Simon Ouyang",
        "url": "https://www.linkedin.com/in/xi-ouyang",
        "email": "simonouyang@gmail.com",
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
    "/",
    summary="Homepage",
    description="Welcome page with API information and links to documentation.",
    response_description="HTML homepage",
    tags=["System"],
    include_in_schema=False,  # Hide from OpenAPI docs
)
async def homepage():
    """Serve the API homepage."""
    from fastapi.responses import HTMLResponse
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Medication Leaflet QA System - Healthcare RAG API</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
                animation: fadeIn 0.6s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            h1 {{
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            .subtitle {{
                color: #666;
                font-size: 1.1em;
                margin-bottom: 30px;
            }}
            .badges {{
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}
            .badge {{
                display: inline-block;
                padding: 6px 12px;
                background: #667eea;
                color: white;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .features {{
                margin: 30px 0;
            }}
            .feature {{
                display: flex;
                align-items: start;
                margin-bottom: 15px;
                padding: 15px;
                background: #f8f9ff;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .feature-icon {{
                font-size: 1.5em;
                margin-right: 15px;
            }}
            .feature-text {{
                flex: 1;
            }}
            .feature-title {{
                font-weight: 600;
                color: #667eea;
                margin-bottom: 5px;
            }}
            .links {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }}
            .link-card {{
                display: block;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .link-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }}
            .link-icon {{
                font-size: 2em;
                display: block;
                margin-bottom: 10px;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Medication Leaflet QA System</h1>
            <p class="subtitle">Production-ready RAG system for healthcare drug-label Q&A</p>
            
            <div class="badges">
                <span class="badge">FastAPI</span>
                <span class="badge">LangGraph</span>
                <span class="badge">Redis Stack</span>
                <span class="badge">W&B</span>
                <span class="badge">OpenAI</span>
            </div>

            <div class="features">
                <div class="feature">
                    <div class="feature-icon">✅</div>
                    <div class="feature-text">
                        <div class="feature-title">Grounded Answers Only</div>
                        Every claim includes citation with source section and URL
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔄</div>
                    <div class="feature-text">
                        <div class="feature-title">LangGraph Agent</div>
                        Multi-node verification pipeline with confidence checks
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-text">
                        <div class="feature-title">Redis Stack HNSW</div>
                        Vector search with metadata filtering for fast retrieval
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <div class="feature-text">
                        <div class="feature-title">W&B Observability</div>
                        Continuous evaluation with regression gates
                    </div>
                </div>
            </div>

            <div class="links">
                <a href="/docs" class="link-card">
                    <span class="link-icon">📚</span>
                    API Documentation
                </a>
                <a href="/health" class="link-card">
                    <span class="link-icon">💚</span>
                    Health Check
                </a>
                <a href="/stats" class="link-card">
                    <span class="link-icon">📈</span>
                    System Stats
                </a>
                <a href="https://github.com/souyang/medication-leaflet-qa-system" target="_blank" class="link-card">
                    <span class="link-icon">⭐</span>
                    Star on GitHub
                </a>
            </div>

            <div class="footer">
                <p><strong>Copyright © {datetime.now().year} Simon Ouyang. All rights reserved.</strong></p>
                <p style="margin-top: 10px;">
                    <a href="https://www.linkedin.com/in/xi-ouyang" target="_blank">LinkedIn</a> • 
                    <a href="https://github.com/souyang" target="_blank">GitHub</a> • 
                    <a href="mailto:simonouyang@gmail.com">Contact</a>
                </p>
                <p style="margin-top: 10px; color: #999; font-size: 0.85em;">
                    ⚠️ Not medical advice. For informational purposes only.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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
