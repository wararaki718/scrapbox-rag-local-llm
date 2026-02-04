from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.encoder_service import EncoderService
from app.services.elasticsearch_service import ElasticsearchService
from app.services.llm_service import LLMService
import json
import asyncio

router = APIRouter()
es_service = ElasticsearchService()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@router.post("/search", response_model=SearchResponse)
async def search_rag(request: SearchRequest):
    # 1. Encode query
    try:
        query_vector = await EncoderService.encode(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoder error: {str(e)}")

    # 2. Search Elasticsearch
    try:
        contexts = await es_service.search(query_vector, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    if not contexts:
        return SearchResponse(answer="関連する情報が見つかりませんでした。", sources=[])

    # 3. Generate Answer
    answer = await LLMService.generate_answer(request.query, contexts)

    return SearchResponse(
        answer=answer,
        sources=contexts
    )

@router.post("/search/stream")
async def search_rag_stream(request: SearchRequest):
    async def event_generator():
        # 1. Encode query
        try:
            query_vector = await EncoderService.encode(request.query)
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Encoder error: {str(e)}'})}\n\n"
            return

        # 2. Search Elasticsearch
        try:
            contexts = await es_service.search(query_vector, top_k=request.top_k)
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Search error: {str(e)}'})}\n\n"
            return

        # Send sources first
        yield f"data: {json.dumps({'sources': contexts})}\n\n"

        if not contexts:
            yield f"data: {json.dumps({'answer': '関連する情報が見つかりませんでした。'})}\n\n"
            return

        # 3. Generate Answer (Stream)
        try:
            async for token in LLMService.generate_answer_stream(request.query, contexts):
                yield f"data: {json.dumps({'answer': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Generation error: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
