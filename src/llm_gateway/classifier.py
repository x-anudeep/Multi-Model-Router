from __future__ import annotations

from llm_gateway.models import ChatRequest, TaskType


class RequestClassifier:
    """Lightweight task classifier with explicit user override support."""

    KEYWORDS: dict[TaskType, tuple[str, ...]] = {
        TaskType.VISION: ("image", "screenshot", "diagram", "photo", "vision", "ocr"),
        TaskType.CODING: ("code", "bug", "function", "class", "api", "python", "sql", "stack trace"),
        TaskType.REASONING: ("prove", "analyze", "reason", "tradeoff", "why", "strategy"),
        TaskType.SUMMARIZATION: ("summarize", "tl;dr", "brief", "extract", "condense"),
        TaskType.EMBEDDING: ("embed", "vector", "semantic search", "similarity"),
    }

    def classify(self, request: ChatRequest) -> TaskType:
        if request.task_type:
            return request.task_type

        prompt = request.prompt.lower()
        scores = {
            task: sum(1 for keyword in keywords if keyword in prompt)
            for task, keywords in self.KEYWORDS.items()
        }
        task, score = max(scores.items(), key=lambda item: item[1])
        return task if score > 0 else TaskType.CHAT

