// aiassistant_dock.js — AI Research Assistant dock panel
// Provides a query interface for the right-side AI assistant panel

const API_BASE = window.API_BASE || "";

/**
 * Initialize the AI assistant dock panel with query input and response area.
 */
export function initAiDock() {
  const container = document.getElementById("aiassistant-dock");
  if (!container) return;

  container.innerHTML = `
    <div class="flex flex-col h-full">
      <!-- Header -->
      <div class="p-4 border-b border-surface-border">
        <h3 class="text-sm font-bold text-gold uppercase tracking-wider flex items-center gap-2">
          <span class="material-symbols-outlined text-base">smart_toy</span>
          AI Research Assistant
        </h3>
        <p class="text-xs text-muted mt-1">Ask anything about Indian equities</p>
      </div>

      <!-- Response Area -->
      <div id="ai-response-area" class="flex-1 overflow-y-auto p-4 space-y-3">
        <div class="text-center text-muted py-8">
          <span class="material-symbols-outlined text-4xl mb-2 block text-gold/40">psychology</span>
          <p class="text-xs">Enter a research query below to get AI-powered insights with deterministic evidence grounding.</p>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-4 border-t border-surface-border">
        <div class="flex gap-2">
          <input
            id="ai-query-input"
            type="text"
            class="form-input flex-1 text-xs"
            placeholder="e.g., Analyze RELIANCE growth drivers..."
            maxlength="500"
          />
          <button id="ai-send-btn" class="btn-primary text-xs px-3" onclick="window.__ierlSendAiQuery()">
            <span class="material-symbols-outlined text-sm">send</span>
          </button>
        </div>
        <div class="flex items-center justify-between mt-2 text-xs text-muted">
          <span>Mode: Quick</span>
          <span id="ai-usage-counter">—</span>
        </div>
      </div>
    </div>`;

  // Attach global send handler
  window.__ierlSendAiQuery = sendQuery;

  // Enter key support
  const input = document.getElementById("ai-query-input");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    });
  }
}

async function sendQuery() {
  const input = document.getElementById("ai-query-input");
  const responseArea = document.getElementById("ai-response-area");
  if (!input || !responseArea) return;

  const query = input.value.trim();
  if (!query) return;

  // Show user query
  responseArea.innerHTML += `
    <div class="p-3 bg-surface-high rounded-lg text-xs text-white">
      <span class="text-gold font-semibold">You:</span> ${escapeHtml(query)}
    </div>`;

  // Show loading
  const loadingId = `ai-loading-${Date.now()}`;
  responseArea.innerHTML += `
    <div id="${loadingId}" class="p-3 bg-surface-low rounded-lg text-xs animate-pulse">
      <span class="text-gold font-semibold">AI:</span> Analyzing...
    </div>`;

  input.value = "";
  responseArea.scrollTop = responseArea.scrollHeight;

  try {
    const resp = await fetch(`${API_BASE}/api/v1/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, mode: "Quick" }),
    });

    const loadingEl = document.getElementById(loadingId);

    if (!resp.ok) {
      if (loadingEl) {
        loadingEl.innerHTML = `
          <span class="text-red font-semibold">Error:</span>
          <span class="text-red/80">Server returned HTTP ${resp.status}. Please try again.</span>`;
        loadingEl.classList.remove("animate-pulse");
      }
      return;
    }

    const data = await resp.json();

    if (loadingEl) {
      const provider = data.provider || "Unknown";
      const disclaimer = data.disclaimer || "";
      loadingEl.innerHTML = `
        <div>
          <span class="text-gold font-semibold">AI (${escapeHtml(provider)}):</span>
          <div class="mt-1 text-gray-200 leading-relaxed whitespace-pre-wrap">${escapeHtml(data.reply || "No response generated.")}</div>
          ${disclaimer ? `<div class="mt-2 text-xs text-muted italic border-t border-surface-border pt-1">${escapeHtml(disclaimer)}</div>` : ""}
        </div>`;
      loadingEl.classList.remove("animate-pulse");
    }
  } catch (err) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      loadingEl.innerHTML = `
        <span class="text-red font-semibold">Error:</span>
        <span class="text-red/80">${escapeHtml(err.message || "Network error")}</span>`;
      loadingEl.classList.remove("animate-pulse");
    }
  }

  responseArea.scrollTop = responseArea.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
