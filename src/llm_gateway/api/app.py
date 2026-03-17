from __future__ import annotations

import json
from collections.abc import Iterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from llm_gateway.adapters import ProviderError
from llm_gateway.config import MODEL_CATALOG
from llm_gateway.gateway import LLMGateway
from llm_gateway.models import ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(
    title="Enterprise LLM Gateway",
    version="0.1.0",
    description="Provider-agnostic LLM gateway with routing, fallback, and cost telemetry.",
)
gateway = LLMGateway()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "unhealthy_models": gateway.metrics()["unhealthy_models"]}


@app.get("/v1/models")
def models() -> list[dict]:
    return [
        {
            "provider": model.provider.value,
            "model": model.model,
            "capabilities": sorted(capability.value for capability in model.capabilities),
            "p50_latency_ms": model.p50_latency_ms,
            "input_cost_per_1k": model.input_cost_per_1k,
            "output_cost_per_1k": model.output_cost_per_1k,
        }
        for model in MODEL_CATALOG
    ]


@app.get("/v1/metrics")
def metrics() -> dict:
    return gateway.metrics()


@app.post("/v1/chat/completions", response_model=ChatResponse)
def completions(request: ChatRequest):
    try:
        response = gateway.complete(request)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if request.stream:
        return StreamingResponse(_stream_response(response), media_type="application/x-ndjson")
    return response


def _stream_response(response: ChatResponse) -> Iterator[str]:
    words = response.content.split()
    for word in words:
        yield json.dumps(
            {
                "request_id": response.request_id,
                "provider": response.provider.value,
                "model": response.model,
                "delta": word + " ",
            }
        ) + "\n"
    yield json.dumps({"request_id": response.request_id, "done": True}) + "\n"


def main() -> None:
    import uvicorn

    uvicorn.run("llm_gateway.api.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()

