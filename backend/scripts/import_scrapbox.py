import asyncio
import json
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

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
        for chunk in batch:
            try:
                chunk.sparse_vector = await EncoderService.encode(chunk.text)
            except Exception as e:
                logger.warning(f"Failed to encode chunk {chunk.id}: {e}")
        await es_service.bulk_index_chunks(batch)
        logger.info(f"Progress: {i + len(batch)}/{len(all_chunks)}")

    logger.info("Import completed successfully!")

async def run_import_api(project_name: str, connect_sid: Optional[str] = None):
    es_service = ElasticsearchService()
    try:
        data = await ScrapboxService.fetch_project_data(project_name, connect_sid)
    except Exception as e:
        logger.error(f"Failed to fetch data from Scrapbox API: {e}")
        return
    
    project = ScrapboxProject(**data)
    await es_service.create_index_if_not_exists()

    all_chunks = []
    for page in project.pages:
        chunks = ScrapboxService.chunk_page(page, project.name)
        all_chunks.extend(chunks)

    logger.info(f"Importing {len(all_chunks)} chunks from API: {project.name}")

    batch_size = 20
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        for chunk in batch:
            try:
                chunk.sparse_vector = await EncoderService.encode(chunk.text)
            except Exception as e:
                logger.warning(f"Failed to encode chunk {chunk.id}: {e}")
        await es_service.bulk_index_chunks(batch)
        logger.info(f"Progress: {i + len(batch)}/{len(all_chunks)}")

    logger.info("Import completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Scrapbox data")
    parser.add_argument("--json", help="Path to JSON file")
    parser.add_argument("--project", help="Scrapbox project name")
    parser.add_argument("--sid", help="Scrapbox connect.sid cookie for private projects")
    
    args = parser.parse_args()
    
    if args.json:
        asyncio.run(run_import(args.json))
    elif args.project:
        asyncio.run(run_import_api(args.project, args.sid))
    else:
        parser.print_help()
        sys.exit(1)
