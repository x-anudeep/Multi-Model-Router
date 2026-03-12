from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    CHAT = "chat"
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    SUMMARIZATION = "summarization"
    EMBEDDING = "embedding"


class ProviderName(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    BEDROCK = "bedrock"


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1)
    task_type: TaskType | None = None
    max_tokens: int = Field(default=512, ge=1, le=8192)
    stream: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class ChatResponse(BaseModel):
    request_id: str
    provider: ProviderName
    model: str
    task_type: TaskType
    content: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: float
    fallback_depth: int = 0
    success: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ModelConfig(BaseModel):
    provider: ProviderName
    model: str
    capabilities: set[TaskType]
    input_cost_per_1k: float
    output_cost_per_1k: float
    p50_latency_ms: int
    priority: int = 100


class RouteDecision(BaseModel):
    candidates: list[ModelConfig]
    reason: str


class LedgerRecord(BaseModel):
    request_id: str
    provider: ProviderName
    model: str
    task_type: TaskType
    success: bool
    fallback_depth: int
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
