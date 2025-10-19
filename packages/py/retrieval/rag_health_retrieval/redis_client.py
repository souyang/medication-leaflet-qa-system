"""Redis client for vector search and document storage."""

import contextlib
import hashlib

import redis
from rag_health_core import ChunkMetadata, RetrievedContext, Settings
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query


class RedisClient:
    """Redis client with vector search capabilities."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Redis client."""
        self.settings = settings
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=False,  # Handle binary for embeddings
        )
        self.index_name = settings.redis_index_name

    def ping(self) -> bool:
        """Check Redis connection."""
        try:
            return self.client.ping()
        except Exception:
            return False

    def create_index(self, drop_existing: bool = False) -> None:
        """Create RediSearch index with HNSW vector field.

        Key pattern: doc:{setid}:{section}:{version}:{hash}
        """
        if drop_existing:
            with contextlib.suppress(Exception):
                self.client.ft(self.index_name).dropindex(delete_documents=True)

        schema = (
            TagField("$.drug_name", as_name="drug"),
            TagField("$.section", as_name="section"),
            NumericField("$.version", as_name="version"),
            TextField("$.text", as_name="text"),
            VectorField(
                "$.emb",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.settings.openai_embedding_dim,
                    "DISTANCE_METRIC": "COSINE",
                    "M": 16,
                    "EF_RUNTIME": 200,
                },
                as_name="emb",
            ),
        )

        definition = IndexDefinition(prefix=["doc:"], index_type=IndexType.JSON)
        self.client.ft(self.index_name).create_index(
            fields=schema,
            definition=definition,
        )

    def upsert_chunk(self, chunk: ChunkMetadata, embedding: list[float]) -> str:
        """Insert or update a document chunk with embedding.

        Returns the Redis key.
        """
        # Generate stable key
        content_hash = hashlib.sha256(chunk.text.encode()).hexdigest()[:8]
        key = f"doc:{chunk.setid}:{chunk.section}:{chunk.version}:{content_hash}"

        doc = {
            "drug_name": chunk.drug_name,
            "setid": chunk.setid,
            "ndc": chunk.ndc,
            "version": chunk.version,
            "section": chunk.section,
            "section_id": chunk.section_id,
            "url": chunk.url,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "emb": embedding,
        }

        self.client.json().set(key, "$", doc)
        return key

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 6,
        drug_filter: str | None = None,
        section_filter: list[str] | None = None,
    ) -> list[RetrievedContext]:
        """Perform KNN vector search with optional filters."""
        # Build query with filters
        filters = []
        if drug_filter:
            filters.append(f"@drug:{{{drug_filter}}}")
        if section_filter:
            section_tags = "|".join(section_filter)
            filters.append(f"@section:{{{section_tags}}}")

        filter_str = " ".join(filters) if filters else "*"

        query = (
            Query(f"({filter_str})=>[KNN {top_k} @emb $vec AS score]")
            .return_fields("drug_name", "section", "section_id", "url", "text", "score")
            .sort_by("score")
            .dialect(2)
        )

        params = {"vec": self._serialize_vector(query_embedding)}

        try:
            results = self.client.ft(self.index_name).search(query, query_params=params)
        except Exception as e:
            raise RuntimeError(f"Redis search failed: {e}") from e

        contexts = []
        seen_sections = set()

        for doc in results.docs:
            section_id = doc.section_id
            # Dedupe by section_id
            if section_id in seen_sections:
                continue
            seen_sections.add(section_id)

            contexts.append(
                RetrievedContext(
                    text=doc.text,
                    section=doc.section,
                    section_id=section_id,
                    url=doc.url,
                    score=1.0 - float(doc.score),  # Cosine distance -> similarity
                )
            )

        return contexts

    def _serialize_vector(self, vec: list[float]) -> bytes:
        """Serialize float vector to bytes."""
        import struct

        return struct.pack(f"{len(vec)}f", *vec)

    def count_documents(self) -> int:
        """Count total documents in index."""
        try:
            info = self.client.ft(self.index_name).info()
            return int(info["num_docs"])
        except Exception:
            return 0
