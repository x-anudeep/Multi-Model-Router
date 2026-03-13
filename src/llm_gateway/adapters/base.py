from __future__ import annotations

from abc import ABC, abstractmethod

from llm_gateway.models import ChatRequest, ModelConfig


class ProviderError(RuntimeError):
    pass


class ProviderAdapter(ABC):
    provider: str

    @abstractmethod
    def complete(self, request: ChatRequest, model: ModelConfig) -> tuple[str, int, int]:
        """Return content, input token estimate, and output token estimate."""


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) + len(text) // 16)

