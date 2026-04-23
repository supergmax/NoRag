"""Async wrapper around google-genai with JSON-mode helper."""

import json
import re
from dataclasses import dataclass
from google import genai
from google.genai import types


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LLMClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=api_key)

    async def _raw_generate(self, model: str, system: str, user: str,
                            response_mime_type: str | None = None):
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type=response_mime_type,
        )
        return await self._client.aio.models.generate_content(
            model=model, contents=user, config=config
        )

    async def generate(self, model: str, system: str, user: str) -> LLMResponse:
        resp = await self._raw_generate(model, system, user)
        return LLMResponse(
            text=resp.text or "",
            tokens=getattr(resp.usage_metadata, "total_token_count", 0),
        )

    async def generate_json(self, model: str, system: str, user: str) -> tuple[dict, LLMResponse]:
        resp = await self._raw_generate(model, system, user,
                                        response_mime_type="application/json")
        text = resp.text or ""
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON found in response: {text[:200]}")
            parsed = json.loads(match.group(0))
        return parsed, LLMResponse(
            text=text,
            tokens=getattr(resp.usage_metadata, "total_token_count", 0),
        )
