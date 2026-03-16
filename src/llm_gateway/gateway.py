from __future__ import annotations

import time

from llm_gateway.adapters import (
    AnthropicAdapter,
    BedrockAdapter,
    CohereAdapter,
    GoogleAdapter,
    MockProviderAdapter,
    OpenAIAdapter,
    ProviderAdapter,
    ProviderError,
)
from llm_gateway.circuit_breaker import CircuitBreaker
from llm_gateway.classifier import RequestClassifier
from llm_gateway.config import MODEL_CATALOG, GatewaySettings
from llm_gateway.ledger import SQLiteLedger
from llm_gateway.models import ChatRequest, ChatResponse, LedgerRecord, ModelConfig, ProviderName
from llm_gateway.router import RoutingPolicy


class LLMGateway:
    def __init__(
        self,
        settings: GatewaySettings | None = None,
        catalog: list[ModelConfig] | None = None,
        adapters: dict[ProviderName, ProviderAdapter] | None = None,
    ) -> None:
        self.settings = settings or GatewaySettings()
        self.catalog = catalog or MODEL_CATALOG
        self.classifier = RequestClassifier()
        self.router = RoutingPolicy(self.catalog)
        self.ledger = SQLiteLedger(self.settings.database_path)
        self.circuit_breaker = CircuitBreaker(
            self.settings.circuit_failure_threshold,
            self.settings.circuit_cooldown_seconds,
        )
        self.adapters = adapters or self._default_adapters()

    def complete(self, request: ChatRequest) -> ChatResponse:
        task_type = self.classifier.classify(request)
        normalized_request = request.model_copy(update={"task_type": task_type})
        route = self.router.route(task_type, self.circuit_breaker.unhealthy_models())

        last_error: ProviderError | None = None
        for fallback_depth, model in enumerate(route.candidates):
            started = time.perf_counter()
            adapter = self.adapters[model.provider]
            try:
                content, input_tokens, output_tokens = adapter.complete(normalized_request, model)
                latency_ms = (time.perf_counter() - started) * 1000
                cost = self.router.estimate_cost(model, input_tokens, output_tokens)
                self.circuit_breaker.record_success(model.model)

                response = ChatResponse(
                    request_id=request.request_id,
                    provider=model.provider,
                    model=model.model,
                    task_type=task_type,
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    estimated_cost_usd=cost,
                    latency_ms=round(latency_ms, 2),
                    fallback_depth=fallback_depth,
                )
                self.ledger.record(
                    LedgerRecord(
                        request_id=response.request_id,
                        provider=response.provider,
                        model=response.model,
                        task_type=response.task_type,
                        success=True,
                        fallback_depth=response.fallback_depth,
                        latency_ms=response.latency_ms,
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens,
                        estimated_cost_usd=response.estimated_cost_usd,
                    )
                )
                return response
            except ProviderError as exc:
                latency_ms = (time.perf_counter() - started) * 1000
                last_error = exc
                self.circuit_breaker.record_failure(model.model)
                self.ledger.record(
                    LedgerRecord(
                        request_id=request.request_id,
                        provider=model.provider,
                        model=model.model,
                        task_type=task_type,
                        success=False,
                        fallback_depth=fallback_depth,
                        latency_ms=round(latency_ms, 2),
                        input_tokens=0,
                        output_tokens=0,
                        estimated_cost_usd=0,
                        error=str(exc),
                    )
                )

        raise ProviderError(f"all fallback providers failed: {last_error}")

    def metrics(self) -> dict:
        return {
            "summary": self.ledger.summary(),
            "recent": self.ledger.recent(),
            "unhealthy_models": sorted(self.circuit_breaker.unhealthy_models()),
        }

    def _default_adapters(self) -> dict[ProviderName, ProviderAdapter]:
        if self.settings.use_mocks:
            mock = MockProviderAdapter()
            return {provider: mock for provider in ProviderName}
        return {
            ProviderName.OPENAI: OpenAIAdapter(),
            ProviderName.ANTHROPIC: AnthropicAdapter(),
            ProviderName.GOOGLE: GoogleAdapter(),
            ProviderName.COHERE: CohereAdapter(),
            ProviderName.BEDROCK: BedrockAdapter(),
        }

