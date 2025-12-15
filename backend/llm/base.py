from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """LLM interface.

    IMPORTANT: LLM is only used for extraction + drafting.
    All calculations (e.g. LVR) and triage decisions must remain deterministic.
    """

    @abstractmethod
    async def complete_json(
        self,
        *,
        prompt: str,
        schema_name: str,
    ) -> dict:
        """Return a JSON object matching the requested schema."""
        raise NotImplementedError
