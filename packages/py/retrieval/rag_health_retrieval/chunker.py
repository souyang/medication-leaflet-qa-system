"""Text chunking utilities."""

import tiktoken


def chunk_text(
    text: str,
    chunk_size: int = 1536,
    overlap: int = 150,
    encoding_name: str = "cl100k_base",
) -> list[str]:
    """Chunk text by token count with overlap.

    Args:
        text: Input text to chunk
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks
        encoding_name: Tiktoken encoding

    Returns:
        List of text chunks
    """
    if not text.strip():
        return []

    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(text)

    if len(tokens) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

        if end >= len(tokens):
            break

        start = end - overlap

    return chunks
