"""Tests for core types."""

import pytest
from rag_health_core import ChunkMetadata, QueryRequest, RetrievedContext


def test_chunk_metadata_creation():
    """Test ChunkMetadata model creation."""
    chunk = ChunkMetadata(
        drug_name="metformin",
        setid="abc123",
        ndc=["12345-678-90"],
        version=1,
        section="DOSAGE_AND_ADMINISTRATION",
        section_id="34068-7",
        url="https://example.com",
        text="Test content",
        chunk_index=0,
    )

    assert chunk.drug_name == "metformin"
    assert chunk.section == "DOSAGE_AND_ADMINISTRATION"
    assert chunk.chunk_index == 0


def test_retrieved_context_citation():
    """Test citation formatting."""
    ctx = RetrievedContext(
        text="Test text",
        section="CONTRAINDICATIONS",
        section_id="34070-3",
        url="https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=abc123",
        score=0.95,
    )

    citation = ctx.citation()
    assert "[Section: CONTRAINDICATIONS]" in citation
    assert "https://dailymed.nlm.nih.gov" in citation
    assert "#section=34070-3" in citation


def test_query_request_validation():
    """Test QueryRequest validation."""
    # Valid request
    req = QueryRequest(query="What is the dose?", drug="metformin", top_k=5)
    assert req.query == "What is the dose?"
    assert req.drug == "metformin"
    assert req.top_k == 5

    # Empty query should fail
    with pytest.raises(ValueError):
        QueryRequest(query="", drug="metformin")

    # top_k out of range
    with pytest.raises(ValueError):
        QueryRequest(query="test", top_k=0)
