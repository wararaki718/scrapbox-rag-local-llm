from elasticsearch import AsyncElasticsearch, helpers
from app.core.config import settings
from app.models.scrapbox import ScrapboxChunk
from typing import List, Dict, Any
from loguru import logger

class ElasticsearchService:
    def __init__(self):
        self.client = AsyncElasticsearch(
            settings.ES_HOST,
            basic_auth=(settings.ES_USER, settings.ES_PASSWORD) if settings.ES_USER else None
        )

    async def create_index_if_not_exists(self):
        index = settings.ES_INDEX
        if await self.client.indices.exists(index=index):
            return

        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "kuromoji_analyzer": {
                            "type": "custom",
                            "tokenizer": "kuromoji_tokenizer"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "page_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "kuromoji_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "kuromoji_analyzer"
                    },
                    "url": {"type": "keyword", "index": False},
                    "updated": {"type": "date", "format": "epoch_second"},
                    "sparse_vector": {"type": "rank_features"}
                }
            }
        }
        await self.client.indices.create(index=index, body=mapping)
        logger.info(f"Created index {index}")

    async def bulk_index_chunks(self, chunks: List[ScrapboxChunk]):
        actions = [
            {
                "_index": settings.ES_INDEX,
                "_id": chunk.id,
                "_source": {
                    "page_id": chunk.page_id,
                    "title": chunk.title,
                    "text": chunk.text,
                    "url": chunk.url,
                    "updated": chunk.updated,
                    "sparse_vector": chunk.sparse_vector
                }
            }
            for chunk in chunks if chunk.sparse_vector
        ]
        if actions:
            await helpers.async_bulk(self.client, actions)
            logger.info(f"Indexed {len(actions)} chunks")

    async def search(self, query_vector: Dict[str, float], top_k: int = 5) -> List[Dict[str, Any]]:
        index = settings.ES_INDEX
        
        # Construct the query using rank_features
        # We use a bool query with multiple rank_feature queries or a single one if ES supports it
        # Actually, for SPLADE, we often use the 'script_score' or 'rank_feature' queries.
        
        should_clauses = [
            {"rank_feature": {"field": "sparse_vector", "boost": weight, "log": {"scaling_factor": 1.0}}}
            for token, weight in query_vector.items()
        ]

        # Note: If too many tokens, this might hit limits. SPLADE usually has dozens/hundreds of tokens.
        # Elasticsearch 8.x supports sparse_vector search more natively in some versions, 
        # but rank_features is the classical way for SPLADE.

        query = {
            "query": {
                "bool": {
                    "should": should_clauses[:1024] # ES limit for should clauses
                }
            },
            "_source": ["title", "text", "url", "updated"]
        }

        response = await self.client.search(index=index, body=query, size=top_k)
        hits = response["hits"]["hits"]
        return [
            {
                "score": hit["_score"],
                "title": hit["_source"]["title"],
                "text": hit["_source"]["text"],
                "url": hit["_source"]["url"],
                "updated": hit["_source"]["updated"]
            }
            for hit in hits
        ]
