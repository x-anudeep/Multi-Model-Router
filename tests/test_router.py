from llm_gateway.config import MODEL_CATALOG
from llm_gateway.models import TaskType
from llm_gateway.router import RoutingPolicy


def test_router_returns_three_tier_fallback_chain() -> None:
    decision = RoutingPolicy(MODEL_CATALOG).route(TaskType.REASONING)

    assert 1 <= len(decision.candidates) <= 3
    assert TaskType.REASONING in decision.candidates[0].capabilities


def test_router_skips_unhealthy_models() -> None:
    decision = RoutingPolicy(MODEL_CATALOG).route(TaskType.VISION, unhealthy_models={"gpt-4o"})

    assert all(model.model != "gpt-4o" for model in decision.candidates)
