from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.encoder_service import EncoderService
from app.services.elasticsearch_service import ElasticsearchService
from app.services.llm_service import LLMService

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
