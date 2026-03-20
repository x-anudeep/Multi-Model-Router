from pathlib import Path

import pytest

from llm_gateway.adapters.base import ProviderAdapter, ProviderError
from llm_gateway.config import GatewaySettings
from llm_gateway.gateway import LLMGateway
from llm_gateway.models import ChatRequest, ModelConfig, ProviderName, TaskType


class FailingAdapter(ProviderAdapter):
    provider = "test"

    def complete(self, request: ChatRequest, model: ModelConfig) -> tuple[str, int, int]:
        raise ProviderError("boom")


class PassingAdapter(ProviderAdapter):
    provider = "test"

    def complete(self, request: ChatRequest, model: ModelConfig) -> tuple[str, int, int]:
        return "ok", 4, 2


def test_gateway_routes_and_records_success(tmp_path: Path) -> None:
    gateway = LLMGateway(settings=GatewaySettings(database_path=str(tmp_path / "ledger.db")))

    response = gateway.complete(ChatRequest(prompt="Summarize this", task_type=TaskType.SUMMARIZATION))

    assert response.success is True
    assert response.estimated_cost_usd >= 0
    assert gateway.ledger.summary()["total_requests"] == 1


def test_gateway_falls_back_after_provider_error(tmp_path: Path) -> None:
    catalog = [
        ModelConfig(
            provider=ProviderName.OPENAI,
            model="primary",
            capabilities={TaskType.CHAT},
            input_cost_per_1k=1,
            output_cost_per_1k=1,
            p50_latency_ms=100,
        ),
        ModelConfig(
            provider=ProviderName.ANTHROPIC,
            model="secondary",
            capabilities={TaskType.CHAT},
            input_cost_per_1k=2,
            output_cost_per_1k=2,
            p50_latency_ms=100,
        ),
    ]
    gateway = LLMGateway(
        settings=GatewaySettings(database_path=str(tmp_path / "ledger.db")),
        catalog=catalog,
        adapters={
            ProviderName.OPENAI: FailingAdapter(),
            ProviderName.ANTHROPIC: PassingAdapter(),
            ProviderName.GOOGLE: PassingAdapter(),
            ProviderName.COHERE: PassingAdapter(),
            ProviderName.BEDROCK: PassingAdapter(),
        },
    )

    response = gateway.complete(ChatRequest(prompt="hello"))

    assert response.model == "secondary"
    assert response.fallback_depth == 1
    assert gateway.ledger.summary()["total_requests"] == 2


def test_gateway_raises_when_all_candidates_fail(tmp_path: Path) -> None:
    gateway = LLMGateway(
        settings=GatewaySettings(database_path=str(tmp_path / "ledger.db")),
        adapters={provider: FailingAdapter() for provider in ProviderName},
    )

    with pytest.raises(ProviderError):
        gateway.complete(ChatRequest(prompt="hello"))

