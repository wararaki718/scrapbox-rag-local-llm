import asyncio
import json
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.scrapbox_service import ScrapboxService
from app.services.encoder_service import EncoderService
from app.services.elasticsearch_service import ElasticsearchService
from app.models.scrapbox import ScrapboxProject
from loguru import logger

async def run_import(json_path: str):
    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    project = ScrapboxProject(**data)
    es_service = ElasticsearchService()
    await es_service.create_index_if_not_exists()

    all_chunks = []
    for page in project.pages:
        chunks = ScrapboxService.chunk_page(page, project.name)
        all_chunks.extend(chunks)

    logger.info(f"Importing {len(all_chunks)} chunks from {project.name}")

    batch_size = 20
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        
        # Encode
        for chunk in batch:
            try:
                chunk.sparse_vector = await EncoderService.encode(chunk.text)
            except Exception as e:
                logger.warning(f"Failed to encode chunk {chunk.id}: {e}")
        
        # Index
        await es_service.bulk_index_chunks(batch)
        logger.info(f"Progress: {i + len(batch)}/{len(all_chunks)}")

    logger.info("Import completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_scrapbox.py <path_to_json>")
        sys.exit(1)
    
    asyncio.run(run_import(sys.argv[1]))
