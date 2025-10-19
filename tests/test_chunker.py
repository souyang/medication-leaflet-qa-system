"""Tests for text chunker."""

from rag_health_retrieval import chunk_text


def test_chunk_text_short() -> None:
    """Test chunking of text shorter than chunk size."""
    text = "Short text."
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long() -> None:
    """Test chunking of long text with overlap."""
    # Create text that will require multiple chunks
    text = " ".join([f"Word{i}" for i in range(2000)])
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) > 1
    # Check overlap exists
    if len(chunks) > 1:
        # Some content should appear in adjacent chunks
        assert any(
            chunk1.split()[-1] in chunk2
            for chunk1, chunk2 in zip(chunks[:-1], chunks[1:], strict=False)
        )


def test_chunk_text_empty() -> None:
    """Test chunking empty text."""
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert len(chunks) == 0


def test_chunk_text_whitespace_only():
    """Test chunking whitespace-only text."""
    chunks = chunk_text("   \n\n  ", chunk_size=100, overlap=10)
    assert len(chunks) == 0
