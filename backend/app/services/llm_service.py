import httpx
from typing import List, Dict, Any
from app.core.config import settings
from loguru import logger

class LLMService:
    @staticmethod
    async def generate_answer(query: str, contexts: List[Dict[str, Any]]) -> str:
        """
        Generates an answer using Gemma 3 via Ollama based on the provided contexts.
        """
        context_text = "\n\n".join([
            f"Source: {ctx['title']} ({ctx['url']})\nContent: {ctx['text']}"
            for ctx in contexts
        ])

        prompt = f"""<start_of_turn>user
提供されたScrapboxの情報のみに基づいて、質問に答えてください。
回答は日本語で、根拠となった情報のタイトルとURLを含めてください。

情報:
{context_text}

質問: {query}<end_of_turn>
<start_of_turn>model
"""
        # Gemma 3 Instruct format might differ slightly, but using this as a standard.

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.LLM_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                        }
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json().get("response", "回答を生成できませんでした。")
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"エラーが発生しました: {str(e)}"

    @staticmethod
    async def generate_answer_stream(query: str, contexts: List[Dict[str, Any]]):
        """
        Generates a streaming answer using Gemma 3 via Ollama.
        """
        context_text = "\n\n".join([
            f"Source: {ctx['title']} ({ctx['url']})\nContent: {ctx['text']}"
            for ctx in contexts
        ])

        prompt = f"""<start_of_turn>user
提供されたScrapboxの情報のみに基づいて、質問に答えてください。
回答は日本語で、根拠となった情報のタイトルとURLを含めてください。

情報:
{context_text}

質問: {query}<end_of_turn>
<start_of_turn>model
"""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.LLM_MODEL,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                        }
                    },
                    timeout=120.0
                ) as response:
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done"):
                            break
        except Exception as e:
            logger.error(f"Error in LLM stream: {e}")
            yield f"\n[Error: {str(e)}]"
