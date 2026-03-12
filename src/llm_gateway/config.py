from __future__ import annotations

import os
from dataclasses import dataclass

from llm_gateway.models import ModelConfig, ProviderName, TaskType


MODEL_CATALOG: list[ModelConfig] = [
    ModelConfig(
        provider=ProviderName.OPENAI,
        model="gpt-4o",
        capabilities={TaskType.CHAT, TaskType.REASONING, TaskType.CODING, TaskType.VISION},
        input_cost_per_1k=0.005,
        output_cost_per_1k=0.015,
        p50_latency_ms=1400,
        priority=10,
    ),
    ModelConfig(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        capabilities={TaskType.CHAT, TaskType.SUMMARIZATION, TaskType.CODING},
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
        p50_latency_ms=650,
        priority=30,
    ),
    ModelConfig(
        provider=ProviderName.ANTHROPIC,
        model="claude-3-5-sonnet",
        capabilities={TaskType.CHAT, TaskType.REASONING, TaskType.CODING, TaskType.SUMMARIZATION},
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        p50_latency_ms=1250,
        priority=8,
    ),
    ModelConfig(
        provider=ProviderName.ANTHROPIC,
        model="claude-3-haiku",
        capabilities={TaskType.CHAT, TaskType.SUMMARIZATION},
        input_cost_per_1k=0.00025,
        output_cost_per_1k=0.00125,
        p50_latency_ms=520,
        priority=25,
    ),
    ModelConfig(
        provider=ProviderName.GOOGLE,
        model="gemini-1.5-pro",
        capabilities={TaskType.CHAT, TaskType.REASONING, TaskType.CODING, TaskType.VISION},
        input_cost_per_1k=0.0035,
        output_cost_per_1k=0.0105,
        p50_latency_ms=1300,
        priority=15,
    ),
    ModelConfig(
        provider=ProviderName.COHERE,
        model="command-r-plus",
        capabilities={TaskType.CHAT, TaskType.SUMMARIZATION, TaskType.EMBEDDING},
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        p50_latency_ms=1100,
        priority=20,
    ),
    ModelConfig(
        provider=ProviderName.BEDROCK,
        model="anthropic.claude-3-sonnet",
        capabilities={TaskType.CHAT, TaskType.REASONING, TaskType.CODING},
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        p50_latency_ms=1500,
        priority=18,
    ),
    ModelConfig(
        provider=ProviderName.BEDROCK,
        model="amazon.titan-text-express",
        capabilities={TaskType.CHAT, TaskType.SUMMARIZATION, TaskType.EMBEDDING},
        input_cost_per_1k=0.0008,
        output_cost_per_1k=0.0016,
        p50_latency_ms=780,
        priority=35,
    ),
]


@dataclass(frozen=True)
class GatewaySettings:
    database_path: str = os.getenv("LLM_GATEWAY_DB", ".data/llm_gateway.sqlite3")
    use_mocks: bool = os.getenv("LLM_GATEWAY_USE_MOCKS", "true").lower() == "true"
    circuit_failure_threshold: int = int(os.getenv("LLM_GATEWAY_FAILURE_THRESHOLD", "3"))
    circuit_cooldown_seconds: int = int(os.getenv("LLM_GATEWAY_CIRCUIT_COOLDOWN", "30"))

