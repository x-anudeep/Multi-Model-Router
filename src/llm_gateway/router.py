from __future__ import annotations

from collections.abc import Iterable

from llm_gateway.models import ModelConfig, RouteDecision, TaskType


class RoutingPolicy:
    def __init__(self, catalog: Iterable[ModelConfig]) -> None:
        self.catalog = list(catalog)

    def route(self, task_type: TaskType, unhealthy_models: set[str] | None = None) -> RouteDecision:
        unhealthy_models = unhealthy_models or set()
        capable = [
            model
            for model in self.catalog
            if task_type in model.capabilities and model.model not in unhealthy_models
        ]
        capable.sort(key=self._score)

        if not capable:
            recovery = [model for model in self.catalog if model.model not in unhealthy_models]
            recovery.sort(key=self._score)
            return RouteDecision(candidates=recovery[:3], reason="no exact capability match; using recovery")

        # Three fallback tiers: best candidate, same-capability alternative, low-cost recovery.
        same_capability = capable[:2]
        cheapest_recovery = sorted(
            [model for model in self.catalog if model.model not in unhealthy_models],
            key=lambda model: model.input_cost_per_1k + model.output_cost_per_1k,
        )[:1]

        chain: list[ModelConfig] = []
        for model in [*same_capability, *cheapest_recovery]:
            if model.model not in {existing.model for existing in chain}:
                chain.append(model)

        return RouteDecision(candidates=chain[:3], reason=f"task-aware route for {task_type.value}")

    @staticmethod
    def estimate_cost(model: ModelConfig, input_tokens: int, output_tokens: int) -> float:
        return round(
            (input_tokens / 1000 * model.input_cost_per_1k)
            + (output_tokens / 1000 * model.output_cost_per_1k),
            6,
        )

    @staticmethod
    def _score(model: ModelConfig) -> tuple[float, int, int]:
        blended_cost = model.input_cost_per_1k + model.output_cost_per_1k
        return (blended_cost, model.p50_latency_ms, model.priority)

