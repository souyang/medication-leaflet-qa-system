"""Seed script to ingest sample drugs."""

import argparse
import asyncio
import logging

from app.ingest import IngestionService
from rag_health_core import Settings
from rag_health_retrieval import RedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_DRUGS = [
    "metformin",
    "lisinopril",
    "atorvastatin",
    "levothyroxine",
    "amlodipine",
]


async def main() -> None:
    """Main ingestion routine."""
    parser = argparse.ArgumentParser(description="Ingest drug labels into Redis")
    parser.add_argument(
        "--drug",
        type=str,
        help="Single drug name to ingest",
    )
    parser.add_argument(
        "--create-index",
        action="store_true",
        help="Create Redis index before ingestion",
    )
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop existing index before creating",
    )

    args = parser.parse_args()

    settings = Settings()
    redis_client = RedisClient(settings)
    ingest_service = IngestionService(settings)

    # Create index if requested
    if args.create_index:
        logger.info(f"Creating index: {settings.redis_index_name}")
        redis_client.create_index(drop_existing=args.drop_existing)
        logger.info("✓ Index created")

    # Determine drugs to ingest
    drugs = [args.drug] if args.drug else DEFAULT_DRUGS

    logger.info(f"\nIngesting {len(drugs)} drug(s)...")

    for drug in drugs:
        logger.info(f"\n→ {drug}")
        try:
            count = await ingest_service.ingest_drug(drug)
            logger.info(f"  ✓ Ingested {count} chunks")
        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            import traceback

            traceback.print_exc()

    # Print stats
    total = redis_client.count_documents()
    logger.info(f"\n✓ Total documents in index: {total}")


if __name__ == "__main__":
    asyncio.run(main())
