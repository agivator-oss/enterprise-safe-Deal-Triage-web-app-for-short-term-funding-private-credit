from __future__ import annotations

from backend.core.config import settings
from backend.llm.azure import AzureOpenAIClient
from backend.llm.base import LLMClient
from backend.llm.stub import StubLLMClient


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "azure":
        return AzureOpenAIClient()
    return StubLLMClient()
