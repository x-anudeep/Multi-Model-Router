from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 30) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._states: dict[str, CircuitState] = {}

    def is_open(self, model: str) -> bool:
        state = self._states.get(model)
        if not state or state.opened_at is None:
            return False
        if time.time() - state.opened_at >= self.cooldown_seconds:
            self._states[model] = CircuitState()
            return False
        return True

    def unhealthy_models(self) -> set[str]:
        return {model for model in self._states if self.is_open(model)}

    def record_success(self, model: str) -> None:
        self._states[model] = CircuitState()

    def record_failure(self, model: str) -> None:
        state = self._states.setdefault(model, CircuitState())
        state.failures += 1
        if state.failures >= self.failure_threshold:
            state.opened_at = time.time()

