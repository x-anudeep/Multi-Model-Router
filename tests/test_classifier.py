from llm_gateway.classifier import RequestClassifier
from llm_gateway.models import ChatRequest, TaskType


def test_classifier_respects_explicit_task_type() -> None:
    request = ChatRequest(prompt="hello", task_type=TaskType.VISION)

    assert RequestClassifier().classify(request) == TaskType.VISION


def test_classifier_detects_summarization() -> None:
    request = ChatRequest(prompt="Summarize this long article for an executive brief")

    assert RequestClassifier().classify(request) == TaskType.SUMMARIZATION

