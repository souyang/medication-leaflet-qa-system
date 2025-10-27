"""Integration tests requiring Redis."""

import os

import pytest
from rag_health_core import ChunkMetadata, Settings
from rag_health_retrieval import RedisClient


@pytest.fixture
def settings():
    """Test settings."""
    # Skip if required environment variables are missing
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    return Settings()


@pytest.fixture
def redis_client(settings):
    """Redis client fixture."""
    client = RedisClient(settings)
    if not client.ping():
        pytest.skip("Redis not available")
    return client


@pytest.mark.integration
def test_redis_ping(redis_client):
    """Test Redis connection."""
    assert redis_client.ping() is True


@pytest.mark.integration
def test_redis_upsert_and_search(redis_client, settings):
    """Test upserting and searching documents."""
    # Create test chunk
    chunk = ChunkMetadata(
        drug_name="test_drug",
        setid="test_setid",
        ndc=[],
        version=1,
        section="TEST_SECTION",
        section_id="test-section",
        url="https://example.com",
        text="This is a test document for integration testing.",
        chunk_index=0,
    )

    # Generate dummy embedding
    embedding = [0.1] * settings.openai_embedding_dim

    # Upsert
    key = redis_client.upsert_chunk(chunk, embedding)
    assert key.startswith("doc:")

    # Search
    contexts = redis_client.search(
        query_embedding=embedding,
        top_k=5,
        drug_filter="test_drug",
    )

    assert len(contexts) > 0
    assert contexts[0].text == chunk.text
