"""Core types for the RAG Health system."""

from typing import TypedDict

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata for a single document chunk."""

    drug_name: str = Field(..., description="Normalized drug name")
    setid: str = Field(..., description="SPL SET ID")
    ndc: list[str] = Field(default_factory=list, description="NDC codes")
    version: int = Field(..., description="Version counter for updates")
    section: str = Field(..., description="Section name (e.g., 'DOSAGE_AND_ADMINISTRATION')")
    section_id: str = Field(..., description="Section anchor ID from SPL")
    url: str = Field(..., description="DailyMed URL")
    text: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(default=0, description="Index within section")


class DrugDocument(BaseModel):
    """Parsed drug label document."""

    drug_name: str
    setid: str
    ndc: list[str] = Field(default_factory=list)
    version: int = Field(default=1)
    url: str
    sections: dict[str, str] = Field(
        default_factory=dict, description="Map section_id -> text content"
    )


class RetrievedContext(BaseModel):
    """A single retrieved context chunk with citation."""

    text: str
    section: str
    section_id: str
    url: str
    score: float = Field(default=0.0, description="Similarity score")

    def citation(self) -> str:
        """Format citation for this context."""
        return f"[Section: {self.section}] ({self.url}#section={self.section_id})"


class RAGState(TypedDict, total=False):
    """LangGraph state for RAG pipeline."""

    query: str
    drug: str | None
    target_sections: list[str]
    ctx: list[RetrievedContext]
    draft: str
    confidence: float
    answer: str
    error: str | None


class QueryRequest(BaseModel):
    """Request to /ask endpoint."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        examples=[
            "What is the starting dose for metformin?",
            "What are the side effects of lisinopril?",
            "What are the contraindications for atorvastatin?",
            "What are the drug interactions with aspirin?",
        ],
    )
    drug: str | None = Field(
        None,
        description="Optional drug name filter",
        examples=["metformin", "lisinopril", "atorvastatin"],
    )
    top_k: int = Field(default=6, ge=1, le=20, examples=[6, 8, 10])


class QueryResponse(BaseModel):
    """Response from /ask endpoint."""

    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    contexts: list[RetrievedContext]
    drug: str | None = None
    disclaimer: str = "Not medical advice. Verify via linked label."
