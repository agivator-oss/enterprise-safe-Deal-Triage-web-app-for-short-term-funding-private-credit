from __future__ import annotations

import httpx

from backend.core.config import settings
from backend.llm.base import LLMClient


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI-style adapter.

    No external calls are made unless required env vars are present.
    """

    def __init__(self):
        if not settings.azure_openai_endpoint or not settings.azure_openai_deployment:
            raise RuntimeError("Azure OpenAI endpoint/deployment not configured")
        if not settings.azure_openai_api_key:
            raise RuntimeError("Azure OpenAI API key missing")

    async def complete_json(self, *, prompt: str, schema_name: str) -> dict:
        # Azure OpenAI chat completions: /openai/deployments/{deployment}/chat/completions?api-version=...
        url = (
            f"{settings.azure_openai_endpoint.rstrip('/')}/openai/deployments/"
            f"{settings.azure_openai_deployment}/chat/completions"
        )
        params = {"api-version": settings.azure_openai_api_version}
        headers = {
            "api-key": settings.azure_openai_api_key,
            "Content-Type": "application/json",
        }

        # NOTE: 'no retention' is a policy/config on the Azure resource; we also avoid logging raw prompts.
        payload = {
            "messages": [
                {"role": "system", "content": "Return only strict JSON. No prose."},
                {"role": "user", "content": prompt},
            ],
            "temperature": settings.llm_temperature,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, params=params, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # Azure returns content string; parse as JSON
        content = data["choices"][0]["message"]["content"]
        import json

        return json.loads(content)
