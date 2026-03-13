from __future__ import annotations

import os

from llm_gateway.adapters.base import ProviderAdapter, ProviderError, estimate_tokens
from llm_gateway.models import ChatRequest, ModelConfig, ProviderName


class EnvironmentBackedAdapter(ProviderAdapter):
    api_key_env: str

    def complete(self, request: ChatRequest, model: ModelConfig) -> tuple[str, int, int]:
        if not os.getenv(self.api_key_env):
            raise ProviderError(f"{self.api_key_env} is not configured")

        # The gateway contract is intentionally isolated from vendor SDKs.
        # Swap this method for each official SDK call when production keys are available.
        content = f"[{model.provider.value}:{model.model}] {request.prompt}"
        return content, estimate_tokens(request.prompt), min(request.max_tokens, estimate_tokens(content))


class OpenAIAdapter(EnvironmentBackedAdapter):
    provider = ProviderName.OPENAI.value
    api_key_env = "OPENAI_API_KEY"


class AnthropicAdapter(EnvironmentBackedAdapter):
    provider = ProviderName.ANTHROPIC.value
    api_key_env = "ANTHROPIC_API_KEY"


class GoogleAdapter(EnvironmentBackedAdapter):
    provider = ProviderName.GOOGLE.value
    api_key_env = "GOOGLE_API_KEY"


class CohereAdapter(EnvironmentBackedAdapter):
    provider = ProviderName.COHERE.value
    api_key_env = "COHERE_API_KEY"


class BedrockAdapter(EnvironmentBackedAdapter):
    provider = ProviderName.BEDROCK.value
    api_key_env = "AWS_ACCESS_KEY_ID"

