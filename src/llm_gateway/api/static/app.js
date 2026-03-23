const state = {
  models: [],
  metrics: null,
};

const samples = [
  "Summarize why an enterprise LLM gateway reduces cost and improves reliability.",
  "Analyze whether a latency-first or cost-first routing policy is better for support chat.",
  "Write a Python function that retries an LLM provider with exponential backoff.",
  "Extract the main risks from a vendor migration plan and create an executive brief.",
];

const elements = {
  apiStatus: document.querySelector("#apiStatus"),
  pulse: document.querySelector(".pulse"),
  form: document.querySelector("#requestForm"),
  prompt: document.querySelector("#prompt"),
  taskType: document.querySelector("#taskType"),
  maxTokens: document.querySelector("#maxTokens"),
  sampleButton: document.querySelector("#sampleButton"),
  refreshButton: document.querySelector("#refreshButton"),
  routeTitle: document.querySelector("#routeTitle"),
  fallbackDepth: document.querySelector("#fallbackDepth"),
  responseBody: document.querySelector("#responseBody"),
  taskMeta: document.querySelector("#taskMeta"),
  latencyMeta: document.querySelector("#latencyMeta"),
  costMeta: document.querySelector("#costMeta"),
  tokensMeta: document.querySelector("#tokensMeta"),
  totalRequests: document.querySelector("#totalRequests"),
  successRate: document.querySelector("#successRate"),
  avgLatency: document.querySelector("#avgLatency"),
  totalCost: document.querySelector("#totalCost"),
  modelGrid: document.querySelector("#modelGrid"),
  ledgerRows: document.querySelector("#ledgerRows"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json();
}

function formatCurrency(value) {
  return `$${Number(value || 0).toFixed(6)}`;
}

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function loadHealth() {
  try {
    await api("/health");
    elements.apiStatus.textContent = "Online";
    elements.pulse.classList.add("online");
  } catch (error) {
    elements.apiStatus.textContent = "Offline";
    elements.pulse.classList.remove("online");
  }
}

async function loadModels() {
  state.models = await api("/v1/models");
  elements.modelGrid.innerHTML = state.models
    .map(
      (model) => `
        <article class="model-card">
          <span class="provider-tag">${model.provider}</span>
          <h4>${model.model}</h4>
          <div class="capability-list">
            ${model.capabilities.map((capability) => `<span>${capability}</span>`).join("")}
          </div>
          <div class="model-meta">
            <span>${model.p50_latency_ms} ms</span>
            <span>$${Number(model.input_cost_per_1k + model.output_cost_per_1k).toFixed(4)}/1K</span>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadMetrics() {
  state.metrics = await api("/v1/metrics");
  const summary = state.metrics.summary;

  elements.totalRequests.textContent = Number(summary.total_requests || 0).toLocaleString();
  elements.successRate.textContent = `${summary.success_rate || 0}%`;
  elements.avgLatency.textContent = `${summary.avg_latency_ms || 0} ms`;
  elements.totalCost.textContent = formatCurrency(summary.total_cost_usd);

  const rows = state.metrics.recent || [];
  elements.ledgerRows.innerHTML = rows.length
    ? rows
        .map(
          (row) => `
          <tr>
            <td>${formatTime(row.created_at)}</td>
            <td>${row.provider}</td>
            <td>${row.model}</td>
            <td>${row.task_type}</td>
            <td class="${row.success ? "success" : "error"}">${row.success ? "success" : "failed"}</td>
            <td>${Number(row.latency_ms || 0).toFixed(2)} ms</td>
            <td>${formatCurrency(row.estimated_cost_usd)}</td>
          </tr>
        `
        )
        .join("")
    : `<tr><td colspan="7">No requests recorded yet.</td></tr>`;
}

async function submitPrompt(event) {
  event.preventDefault();
  elements.responseBody.textContent = "Routing request...";

  const taskType = elements.taskType.value || null;
  const payload = {
    prompt: elements.prompt.value.trim(),
    task_type: taskType,
    max_tokens: Number(elements.maxTokens.value),
  };

  try {
    const response = await api("/v1/chat/completions", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    elements.routeTitle.textContent = `${response.provider} / ${response.model}`;
    elements.fallbackDepth.textContent = `Depth ${response.fallback_depth}`;
    elements.responseBody.textContent = response.content;
    elements.taskMeta.textContent = response.task_type;
    elements.latencyMeta.textContent = `${Number(response.latency_ms).toFixed(2)} ms`;
    elements.costMeta.textContent = formatCurrency(response.estimated_cost_usd);
    elements.tokensMeta.textContent = `${response.input_tokens + response.output_tokens}`;

    await loadMetrics();
  } catch (error) {
    elements.routeTitle.textContent = "Request failed";
    elements.responseBody.textContent = error.message;
  }
}

function loadSample() {
  const current = samples.indexOf(elements.prompt.value);
  elements.prompt.value = samples[(current + 1) % samples.length];
}

async function init() {
  elements.form.addEventListener("submit", submitPrompt);
  elements.sampleButton.addEventListener("click", loadSample);
  elements.refreshButton.addEventListener("click", loadMetrics);

  await Promise.all([loadHealth(), loadModels(), loadMetrics()]);
}

init();
