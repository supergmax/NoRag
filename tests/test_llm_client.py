import pytest
from unittest.mock import AsyncMock, patch
from core.llm_client import LLMClient, LLMResponse

@pytest.mark.asyncio
async def test_generate_returns_text_and_tokens():
    client = LLMClient(api_key="test-key")

    fake_response = type("R", (), {
        "text": "hello",
        "usage_metadata": type("U", (), {"total_token_count": 42})(),
    })()

    with patch.object(client, "_raw_generate", new=AsyncMock(return_value=fake_response)):
        resp = await client.generate(model="gemini-2.5-flash-lite",
                                     system="sys",
                                     user="hi")
    assert isinstance(resp, LLMResponse)
    assert resp.text == "hello"
    assert resp.tokens == 42

@pytest.mark.asyncio
async def test_generate_json_parses_output():
    client = LLMClient(api_key="test-key")
    fake_response = type("R", (), {
        "text": '{"agent_id": "foo", "documents": []}',
        "usage_metadata": type("U", (), {"total_token_count": 10})(),
    })()
    with patch.object(client, "_raw_generate", new=AsyncMock(return_value=fake_response)):
        parsed, raw = await client.generate_json(model="gemini-2.5-flash-lite",
                                                 system="sys", user="hi")
    assert parsed == {"agent_id": "foo", "documents": []}
    assert raw.tokens == 10

@pytest.mark.asyncio
async def test_generate_json_extracts_json_from_prose():
    client = LLMClient(api_key="test-key")
    fake_response = type("R", (), {
        "text": 'Sure! Here is the JSON: {"agent_id": "bar", "documents": []}',
        "usage_metadata": type("U", (), {"total_token_count": 15})(),
    })()
    with patch.object(client, "_raw_generate", new=AsyncMock(return_value=fake_response)):
        parsed, raw = await client.generate_json(model="gemini-2.5-flash-lite",
                                                 system="sys", user="hi")
    assert parsed["agent_id"] == "bar"
