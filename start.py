#!/usr/bin/env python3
"""
Startup script for Render deployment.
This script handles the initialization sequence for production deployment.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps" / "api"))

# Set up environment
os.environ.setdefault("PYTHONPATH", str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def initialize_services():
    """Initialize services on startup."""
    try:
        # Import here to avoid circular imports
        from rag_health_core import Settings

        from apps.api.app.agent import RAGAgent
        from apps.api.app.ingest import IngestionService

        settings = Settings()

        # Initialize services
        logger.info("Initializing RAG agent...")
        agent = RAGAgent(settings)

        logger.info("Initializing ingestion service...")
        _ = IngestionService(settings)  # Initialize but don't store

        # Test Redis connection
        logger.info("Testing Redis connection...")
        if agent.redis_client.ping():
            logger.info("✓ Redis connected successfully")
        else:
            logger.warning("⚠️ Redis connection failed - service will be degraded")

        logger.info("✓ Services initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False


if __name__ == "__main__":
    # Run initialization
    success = asyncio.run(initialize_services())

    if not success:
        logger.warning("Warning: Some services failed to initialize, but continuing...")

    # Start the FastAPI server
    import uvicorn

    uvicorn.run(
        "apps.api.app.api:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info",
    )
