from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from llm_gateway.gateway import LLMGateway
from llm_gateway.models import ChatRequest, TaskType

load_dotenv()

st.set_page_config(page_title="Enterprise LLM Gateway", page_icon="LLM", layout="wide")

gateway = LLMGateway()

st.title("Enterprise LLM Gateway")
st.caption("Provider routing, fallback health, latency, and cost telemetry")

with st.sidebar:
    st.header("Request Console")
    prompt = st.text_area("Prompt", value="Summarize why a multi-model gateway reduces LLM cost.")
    task = st.selectbox("Task type", ["auto", *[task.value for task in TaskType]])
    max_tokens = st.slider("Max tokens", min_value=64, max_value=2048, value=512, step=64)
    submitted = st.button("Route Request", type="primary")

if submitted:
    request = ChatRequest(
        prompt=prompt,
        task_type=None if task == "auto" else TaskType(task),
        max_tokens=max_tokens,
    )
    response = gateway.complete(request)
    st.success(f"Routed to {response.provider.value} / {response.model}")
    st.write(response.content)

metrics = gateway.metrics()
summary = metrics["summary"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("API Calls", f"{summary['total_requests']:,}")
col2.metric("Success Rate", f"{summary['success_rate']}%")
col3.metric("Avg Latency", f"{summary['avg_latency_ms']} ms")
col4.metric("Total Cost", f"${summary['total_cost_usd']:.6f}")

recent = pd.DataFrame(metrics["recent"])

if recent.empty:
    st.info("No traffic recorded yet. Send a request from the sidebar or FastAPI endpoint.")
else:
    recent["created_at"] = pd.to_datetime(recent["created_at"])
    chart_data = recent.sort_values("created_at")

    left, right = st.columns(2)
    with left:
        st.subheader("Latency by Request")
        st.line_chart(chart_data, x="created_at", y="latency_ms")
    with right:
        st.subheader("Cost by Request")
        st.bar_chart(chart_data, x="created_at", y="estimated_cost_usd")

    st.subheader("Provider Mix")
    provider_mix = recent.groupby("provider").size().reset_index(name="requests")
    st.bar_chart(provider_mix, x="provider", y="requests")

    st.subheader("Request Ledger")
    st.dataframe(
        recent[
            [
                "created_at",
                "request_id",
                "provider",
                "model",
                "task_type",
                "success",
                "fallback_depth",
                "latency_ms",
                "estimated_cost_usd",
                "error",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(f"SQLite ledger: {os.getenv('LLM_GATEWAY_DB', '.data/llm_gateway.sqlite3')}")
