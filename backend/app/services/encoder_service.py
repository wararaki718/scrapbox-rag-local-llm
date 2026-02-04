import httpx
from typing import Dict, List
from app.core.config import settings
from loguru import logger

class EncoderService:
    @staticmethod
    async def encode(text: str) -> Dict[str, float]:
        """
        Sends text to the SPLADE Encoder API and returns the sparse vector.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SPLADE_API_URL,
                    json={"text": text},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                # Assuming the response format is {"indices": [...], "values": [...]} 
                # or a direct dictionary of {token: weight}
                return data.get("vector", data)
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            # Return empty or fall back if possible. For now, raise.
            raise

    @staticmethod
    async def encode_batch(texts: List[str]) -> List[Dict[str, float]]:
        """
        Encodes a batch of texts.
        """
        # Simple sequential for now, can be optimized with asyncio.gather
        results = []
        for text in texts:
            results.append(await EncoderService.encode(text))
        return results
