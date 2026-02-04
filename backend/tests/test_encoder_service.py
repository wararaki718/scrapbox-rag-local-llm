import pytest
from app.services.encoder_service import EncoderService
import httpx

@pytest.mark.asyncio
async def test_encode_success(respx_mock):
    # Mocking the SPLADE API
    respx_mock.post("http://localhost:8001/encode").mock(
        return_value=httpx.Response(200, json={"vector": {"123": 0.5, "456": 0.8}})
    )
    
    result = await EncoderService.encode("hello world")
    assert result == {"123": 0.5, "456": 0.8}

@pytest.mark.asyncio
async def test_encode_failure(respx_mock):
    respx_mock.post("http://localhost:8001/encode").mock(
        return_value=httpx.Response(500)
    )
    
    with pytest.raises(Exception):
        await EncoderService.encode("fail")
