#!/usr/bin/env python3
"""Update copyright year in Postman collection to current year."""

import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_copyright_year():
    """Update copyright year in Postman collection."""
    collection_path = Path("Medication-Leaflet-QA-API.postman_collection.json")

    if not collection_path.exists():
        logger.error(f"Collection file not found: {collection_path}")
        return

    # Read the collection
    with open(collection_path) as f:
        collection = json.load(f)

    # Update copyright year
    current_year = datetime.now().year
    old_copyright = "**Copyright © 2024 Simon Ouyang. All rights reserved.**"
    new_copyright = f"**Copyright © {current_year} Simon Ouyang. All rights reserved.**"

    if old_copyright in collection["info"]["description"]:
        collection["info"]["description"] = collection["info"]["description"].replace(
            old_copyright, new_copyright
        )
        logger.info(f"Updated copyright year to {current_year}")
    else:
        logger.info("Copyright notice not found or already updated")
        return

    # Write back the collection
    with open(collection_path, "w") as f:
        json.dump(collection, f, indent="\t")

    logger.info(f"Successfully updated Postman collection with copyright year {current_year}")


if __name__ == "__main__":
    update_copyright_year()
