from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.services.scrapbox_service import ScrapboxService
from app.services.encoder_service import EncoderService
from app.services.elasticsearch_service import ElasticsearchService
from app.models.scrapbox import ScrapboxProject
import json
from loguru import logger
import asyncio

router = APIRouter()
es_service = ElasticsearchService()

async def process_ingestion(project_data: dict):
    try:
        project = ScrapboxProject(**project_data)
        await es_service.create_index_if_not_exists()
        
        all_chunks = []
        for page in project.pages:
            chunks = ScrapboxService.chunk_page(page, project.name)
            all_chunks.extend(chunks)
        
        logger.info(f"Processing {len(all_chunks)} chunks from project {project.name}")
        
        # Encode chunks in batches to avoid overloading
        batch_size = 10
        semaphore = asyncio.Semaphore(5) # Max 5 concurrent encodes

        async def encode_with_sem(chunk):
            async with semaphore:
                chunk.sparse_vector = await EncoderService.encode(chunk.text)
                return chunk

        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            tasks = [encode_with_sem(c) for c in batch]
            processed_batch = await asyncio.gather(*tasks)
            await es_service.bulk_index_chunks(processed_batch)
            logger.info(f"Progress: {i + len(batch)}/{len(all_chunks)}")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")

@router.post("/ingest")
async def ingest_scrapbox(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    content = await file.read()
    data = json.loads(content)
    
    background_tasks.add_task(process_ingestion, data)
    
    return {"message": "Ingestion started in background"}
