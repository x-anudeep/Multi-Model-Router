from __future__ import annotations

import os

from llm_gateway.adapters.base import ProviderAdapter, ProviderError, estimate_tokens
from llm_gateway.models import ChatRequest, ModelConfig


class MockProviderAdapter(ProviderAdapter):
    def complete(self, request: ChatRequest, model: ModelConfig) -> tuple[str, int, int]:
        failure_key = f"MOCK_FAIL_{model.provider.value.upper()}_{model.model.upper().replace('-', '_').replace('.', '_')}"
        if os.getenv(failure_key) == "true":
            raise ProviderError(f"forced mock failure for {model.model}")

        content = (
            f"[{model.provider.value}:{model.model}] "
            f"Handled {request.task_type or 'auto'} request: {request.prompt[:180]}"
        )
        input_tokens = estimate_tokens(request.prompt)
        output_tokens = min(request.max_tokens, estimate_tokens(content))
        return content, input_tokens, output_tokens

