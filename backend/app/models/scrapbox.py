from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ScrapboxPage(BaseModel):
    id: str
    title: str
    lines: List[str]
    updated: int
    pin: int = 0

class ScrapboxProject(BaseModel):
    name: str
    displayName: str
    pages: List[ScrapboxPage]

class ScrapboxChunk(BaseModel):
    id: str  # unique id for ES: {page_id}_{chunk_index}
    page_id: str
    title: str
    text: str
    url: str
    updated: int
    sparse_vector: Optional[Dict[str, float]] = None
