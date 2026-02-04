import pytest
from fastapi.testclient import TestClient
from app.main import app
import httpx

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Scrapbox RAG API is running"}

@pytest.mark.asyncio
async def test_search_endpoint(respx_mock):
    # Mock Encoder
    respx_mock.post("http://localhost:8001/encode").mock(
        return_value=httpx.Response(200, json={"vector": {"1": 1.0}})
    )
    # Mock Ollama
    respx_mock.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "Bot reply"})
    )
    
    # Mock Elasticsearch search - needs more complex mocking if we use the service directly.
    # For now, we mainly test the routing and LLM flow.
    # Service mocking would be better with pytest-mock.
