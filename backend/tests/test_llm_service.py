import pytest
from app.services.llm_service import LLMService
import httpx

@pytest.mark.asyncio
async def test_generate_answer_success(respx_mock):
    respx_mock.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "This is a test answer."})
    )
    
    contexts = [
        {"title": "Test Title", "text": "Test Context", "url": "http://test.com"}
    ]
    
    answer = await LLMService.generate_answer("What is this?", contexts)
    assert answer == "This is a test answer."

@pytest.mark.asyncio
async def test_generate_answer_error(respx_mock):
    respx_mock.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(500)
    )
    
    answer = await LLMService.generate_answer("Fail", [])
    assert "エラーが発生しました" in answer
