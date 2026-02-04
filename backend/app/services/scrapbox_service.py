import re
import httpx
import urllib.parse
from typing import List, Optional
from app.models.scrapbox import ScrapboxPage, ScrapboxChunk, ScrapboxProject
from loguru import logger

class ScrapboxService:
    @staticmethod
    async def fetch_project_data(project_name: str, connect_sid: Optional[str] = None) -> dict:
        """Fetch all pages from a Scrapbox project via API."""
        base_url = f"https://scrapbox.io/api/pages/{project_name}"
        cookies = {"connect.sid": connect_sid} if connect_sid else {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Get page list
            logger.info(f"Fetching page list for project: {project_name}")
            response = await client.get(f"{base_url}?limit=1000", cookies=cookies)
            response.raise_for_status()
            pages_list = response.json()["pages"]
            
            # 2. Fetch full content for each page
            full_pages = []
            for i, p in enumerate(pages_list):
                page_title = p["title"]
                logger.info(f"Fetching page ({i+1}/{len(pages_list)}): {page_title}")
                
                # Encode title for URL
                encoded_title = urllib.parse.quote(page_title, safe="")
                page_res = await client.get(f"{base_url}/{encoded_title}", cookies=cookies)
                
                if page_res.status_code == 200:
                    page_data = page_res.json()
                    # Convert to our model format (lines is a list of objects in API, but our model expects list[str])
                    lines = [line_obj["text"] for line_obj in page_data.get("lines", [])]
                    full_pages.append({
                        "id": page_data["id"],
                        "title": page_data["title"],
                        "updated": page_data["updated"],
                        "lines": lines
                    })
                
            return {
                "name": project_name,
                "displayName": project_name,
                "pages": full_pages
            }

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
