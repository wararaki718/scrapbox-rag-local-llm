import re
from typing import List
from app.models.scrapbox import ScrapboxPage, ScrapboxChunk

class ScrapboxService:
    @staticmethod
    def clean_scrapbox_text(text: str) -> str:
        # Remove [links], [images.jpg], etc.
        # Simple regex to remove brackets but keep text
        text = re.sub(r'\[([^\]]+)\]', r'\1', text)
        return text.strip()

    @staticmethod
    def chunk_page(page: ScrapboxPage, project_name: str) -> List[ScrapboxChunk]:
        chunks = []
        lines = page.lines
        title = page.title
        page_url = f"https://scrapbox.io/{project_name}/{title.replace(' ', '_')}"
        
        # Simple semantic chunking: grouped by sections or indents
        current_chunk_text = []
        max_chunk_length = 500
        
        for i, line in enumerate(lines):
            # Skip empty lines if chunk is empty
            if not line.strip() and not current_chunk_text:
                continue
            
            clean_line = ScrapboxService.clean_scrapbox_text(line)
            current_chunk_text.append(clean_line)
            
            # If current chunk is long enough or we see a potential break
            if sum(len(l) for l in current_chunk_text) > max_chunk_length:
                text = "\n".join(current_chunk_text)
                chunks.append(ScrapboxChunk(
                    id=f"{page.id}_{len(chunks)}",
                    page_id=page.id,
                    title=title,
                    text=text,
                    url=page_url,
                    updated=page.updated
                ))
                current_chunk_text = []

        # Add remaining text as a chunk
        if current_chunk_text:
            text = "\n".join(current_chunk_text)
            chunks.append(ScrapboxChunk(
                id=f"{page.id}_{len(chunks)}",
                page_id=page.id,
                title=title,
                text=text,
                url=page_url,
                updated=page.updated
            ))
            
        return chunks
