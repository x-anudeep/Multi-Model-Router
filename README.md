# Enterprise LLM Gateway

A provider-agnostic LLM routing layer built with Python, FastAPI, Streamlit, and SQLite. The project is designed to match the resume scope: unified access to 5 LLM platforms, task-aware routing across 8 model configurations, 3-tier fallback handling, and cost/latency observability.

## What It Does

- Exposes one SDK and one FastAPI endpoint for OpenAI, Anthropic, Google, Cohere, and Bedrock style providers.
- Classifies requests into task types such as reasoning, coding, vision, summarization, chat, and embedding.
- Routes by capability, estimated cost, health, and latency policy.
- Applies a 3-tier fallback chain: preferred model, same-capability alternative, then low-cost recovery model.
- Records every request in a SQLite ledger for success rate, latency, tokens, cost, and fallback analysis.
- Ships with a Streamlit dashboard for live gateway metrics.
- Runs locally without API keys using deterministic mock providers.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn llm_gateway.api.app:app --reload
```

In another terminal:

```bash
streamlit run dashboard/app.py
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Summarize the benefits of an LLM gateway","task_type":"summarization"}'
```

## Architecture

```text
Client / SDK
  -> FastAPI gateway
  -> Request classifier
  -> Routing policy
  -> Provider adapter
  -> Circuit breaker + fallback chain
  -> SQLite cost/latency ledger
  -> Streamlit dashboard
```

## Resume Alignment

This project demonstrates an enterprise LLM abstraction layer:

- **5 LLM platforms:** OpenAI, Anthropic, Google, Cohere, Bedrock.
- **8 model configurations:** GPT-4o, GPT-4o Mini, Claude 3.5 Sonnet, Claude 3 Haiku, Gemini 1.5 Pro, Command R+, Bedrock Claude, Bedrock Titan.
- **Task-aware routing:** capability, latency, health, and cost policies.
- **3-tier fallback:** primary, provider/model alternative, final recovery provider.
- **Cost optimization:** lower-cost models are preferred for simple tasks while premium models are reserved for reasoning, coding, and vision.
- **Observability:** SQLite request ledger plus dashboard KPIs.

## Configuration

Copy `.env.example` to `.env` if you want to connect real providers. Without keys, the gateway uses mock adapters so demos and tests remain reproducible.

```bash
cp .env.example .env
```

## Project Layout

```text
src/llm_gateway/
  adapters/       Provider adapter contracts and implementations
  api/            FastAPI application
  classifier.py   Task classifier
  config.py       Model catalog and routing policy
  gateway.py      Orchestration, fallback, and ledger recording
  ledger.py       SQLite telemetry store
  models.py       Shared Pydantic models
  router.py       Capability/cost/latency router
dashboard/app.py  Streamlit dashboard
tests/            Unit and API tests
```

## Four Implementation Phases

1. Foundation and provider abstraction.
2. Routing, fallback, and reliability controls.
3. API, dashboard, and telemetry.
4. Packaging, tests, docs, and resume polish.

