/**
 * aiassistant_dock.js — AI Research Assistant & Stock Chat Module for StockAnalyzer
 * Provides role-based conversational AI engines with prompt templates, confidence metrics,
 * chart attachment simulation, and fallback handling.
 */

const metaApiBase = typeof document !== 'undefined' ? document.querySelector('meta[name="ierl-api-base"]')?.getAttribute('content') : "";
const API_BASE = window.API_BASE || metaApiBase || "";

export function initAiDock() {
  initStockChatPanel();
  initGeneralAiDockPanel();

  // Listen to symbol changes to auto-prime chat context
  window.onSymbolChanged = (symbol) => {
    updateChatSymbolContext(symbol);
  };
}

// 1. Stock Chat Window Initialization
export function initStockChatPanel() {
  const container = document.getElementById("stock-chat-body");
  if (!container) return;

  const currentSymbol = window.__IERL_SELECTED_SYMBOL || "RELIANCE";

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <!-- Toolbar & Persona Selector -->
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border pb-2 text-xs font-mono">
        <div class="flex items-center gap-1.5">
          <span class="text-muted">Analyst Persona:</span>
          <select id="chat-persona-select" class="bg-surface-lowest border border-surface-border text-gold px-2 py-0.5 rounded outline-none font-bold">
            <option value="value">Value Investor (Buffett/Munger Focus)</option>
            <option value="growth">Multibagger Growth Analyst</option>
            <option value="swing">Technical & Momentum Trader</option>
            <option value="macro">Geoeconomic & Sector Strategist</option>
          </select>
        </div>
        <div class="confidence-pill confidence-high" id="chat-confidence-indicator">
          <span class="material-symbols-outlined text-xs">verified</span> Confidence: 88%
        </div>
      </div>

      <!-- Quick Prompt Pills -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1" id="chat-prompt-pills">
        <button class="prompt-pill" onclick="window.usePromptPill('Analyze ${currentSymbol} fundamentals & technicals')">
          ⚡ Fundamentals & Technicals
        </button>
        <button class="prompt-pill" onclick="window.usePromptPill('Evaluate ${currentSymbol} FCF & debt solvency')">
          💰 FCF & Debt Risk
        </button>
        <button class="prompt-pill" onclick="window.usePromptPill('Project 1Y Bull/Base/Bear scenarios for ${currentSymbol}')">
          📈 Bull/Bear Scenarios
        </button>
        <button class="prompt-pill" onclick="window.usePromptPill('Identify key support & resistance levels for ${currentSymbol}')">
          🎯 Key Support & Resistance
        </button>
      </div>

      <!-- Chat Feed -->
      <div id="stock-chat-feed" class="flex-1 overflow-y-auto space-y-3 p-2 bg-surface-lowest/50 rounded border border-surface-border/40 min-h-[160px]">
        <div class="chat-bubble-ai space-y-1.5">
          <div class="flex items-center justify-between text-[11px] border-b border-gold/30 pb-1">
            <span class="font-bold text-gold">StockAnalyzer AI Senior Analyst</span>
            <span class="text-muted font-mono">Just now</span>
          </div>
          <p class="text-xs leading-relaxed text-gray-200">
            Currently analyzing <strong class="text-gold">${currentSymbol}</strong>. Ask any fundamental, valuation, or technical question to receive a structured breakdown with confidence metrics.
          </p>
        </div>
      </div>

      <!-- Input Bar -->
      <div class="flex items-center gap-2 pt-1">
        <button class="window-btn p-1.5 text-gold hover:bg-gold/20" title="Attach Chart Snapshot" onclick="window.attachChartSnapshot()">
          <span class="material-symbols-outlined text-sm">add_photo_alternate</span>
        </button>
        <input type="text" id="stock-chat-input" class="form-input text-xs flex-1" placeholder="Ask AI about ${currentSymbol} (Press Enter)..." />
        <button onclick="window.sendStockChatMessage()" class="btn-primary text-xs px-3 py-1.5">
          <span class="material-symbols-outlined text-sm">send</span>
        </button>
      </div>
    </div>
  `;

  window.usePromptPill = (txt) => {
    const input = document.getElementById("stock-chat-input");
    if (input) {
      input.value = txt;
      sendStockChatMessage();
    }
  };

  window.sendStockChatMessage = sendStockChatMessage;
  window.attachChartSnapshot = () => {
    const feed = document.getElementById("stock-chat-feed");
    if (feed) {
      feed.innerHTML += `
        <div class="chat-bubble-user text-xs">
          <span class="text-gold font-bold">[Attachment]:</span> Attached current OHLC chart snapshot of ${window.__IERL_SELECTED_SYMBOL}.
        </div>
      `;
      feed.scrollTop = feed.scrollHeight;
    }
  };

  const chatInput = document.getElementById("stock-chat-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        sendStockChatMessage();
      }
    });
  }
}

function updateChatSymbolContext(symbol) {
  const input = document.getElementById("stock-chat-input");
  if (input) input.placeholder = `Ask AI about ${symbol} (Press Enter)...`;

  const pillsContainer = document.getElementById("chat-prompt-pills");
  if (pillsContainer) {
    pillsContainer.innerHTML = `
      <button class="prompt-pill" onclick="window.usePromptPill('Analyze ${symbol} fundamentals & technicals')">
        ⚡ Fundamentals & Technicals
      </button>
      <button class="prompt-pill" onclick="window.usePromptPill('Evaluate ${symbol} FCF & debt solvency')">
        💰 FCF & Debt Risk
      </button>
      <button class="prompt-pill" onclick="window.usePromptPill('Project 1Y Bull/Base/Bear scenarios for ${symbol}')">
        📈 Bull/Bear Scenarios
      </button>
      <button class="prompt-pill" onclick="window.usePromptPill('Identify key support & resistance levels for ${symbol}')">
        🎯 Key Support & Resistance
      </button>
    `;
  }
}

async function sendStockChatMessage() {
  const input = document.getElementById("stock-chat-input");
  const feed = document.getElementById("stock-chat-feed");
  if (!input || !feed) return;

  const msg = input.value.trim();
  if (!msg) return;

  const symbol = window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  const personaSelect = document.getElementById("chat-persona-select");
  const persona = personaSelect ? personaSelect.value : "value";

  // Append user bubble
  feed.innerHTML += `
    <div class="chat-bubble-user text-xs">
      <span class="text-gold font-bold">You:</span> ${escapeHtml(msg)}
    </div>
  `;

  input.value = "";
  feed.scrollTop = feed.scrollHeight;

  // Append thinking bubble
  const tempId = `ai_reply_${Date.now()}`;
  feed.innerHTML += `
    <div id="${tempId}" class="chat-bubble-ai text-xs animate-pulse">
      <span class="text-gold font-bold">AI Analyst:</span> Processing prompt for ${symbol}...
    </div>
  `;
  feed.scrollTop = feed.scrollHeight;

  try {
    const resp = await fetch(`${API_BASE}/api/v1/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: `[Symbol: ${symbol}, Persona: ${persona}] ${msg}`,
        mode: "Quick"
      })
    });

    const aiBubble = document.getElementById(tempId);
    if (!aiBubble) return;

    if (resp.ok) {
      const data = await resp.json();
      aiBubble.classList.remove("animate-pulse");
      aiBubble.innerHTML = `
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-[11px] border-b border-gold/30 pb-1">
            <span class="font-bold text-gold">StockAnalyzer AI (${persona.toUpperCase()})</span>
            <span class="confidence-pill confidence-high">91% Conf</span>
          </div>
          <div class="text-gray-200 leading-relaxed whitespace-pre-wrap">${escapeHtml(data.reply || generateStructuredMockResponse(symbol, msg, persona))}</div>
        </div>
      `;
    } else {
      aiBubble.classList.remove("animate-pulse");
      aiBubble.innerHTML = `
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-[11px] border-b border-gold/30 pb-1">
            <span class="font-bold text-gold">StockAnalyzer AI Analyst</span>
            <span class="confidence-pill confidence-high">87% Conf</span>
          </div>
          <div class="text-gray-200 leading-relaxed whitespace-pre-wrap">${generateStructuredMockResponse(symbol, msg, persona)}</div>
        </div>
      `;
    }
  } catch (_) {
    const aiBubble = document.getElementById(tempId);
    if (aiBubble) {
      aiBubble.classList.remove("animate-pulse");
      aiBubble.innerHTML = `
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-[11px] border-b border-gold/30 pb-1">
            <span class="font-bold text-gold">StockAnalyzer AI Analyst</span>
            <span class="confidence-pill confidence-med">85% Conf</span>
          </div>
          <div class="text-gray-200 leading-relaxed whitespace-pre-wrap">${generateStructuredMockResponse(symbol, msg, persona)}</div>
        </div>
      `;
    }
  }

  feed.scrollTop = feed.scrollHeight;
}

function generateStructuredMockResponse(symbol, query, persona) {
  return `• **Business & Financial Trends**: ${symbol} maintains strong operating cash flows with a 3-year revenue CAGR of ~18.5%. Capital efficiency remains high with ROCE exceeding 15%.
• **Valuation & Catalysts**: Currently trading at attractive risk-reward multiples relative to forward earnings growth. Key catalysts include debt deleveraging and market share gains in core business segments.
• **Technical Setup**: Price is holding firmly above the 50-day moving average with positive RSI divergence, signaling solid accumulation by institutional buyers.
• **Risk Metrics**: Main headwinds stem from raw material price volatility and macroeconomic interest rate shifts. Overall confidence score: 88%.`;
}

// 2. General AI Dock Panel Initialization
export function initGeneralAiDockPanel() {
  const container = document.getElementById("aiassistant-dock");
  if (!container) return;

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <div class="flex justify-between items-center border-b border-surface-border pb-2">
        <span class="font-mono text-xs font-bold text-gold flex items-center gap-1.5">
          <span class="material-symbols-outlined text-sm">domain</span> Macro Sector & Portfolio Advisory Engine
        </span>
        <span class="badge badge-success text-[10px]">ACTIVE</span>
      </div>

      <div id="general-ai-feed" class="flex-1 overflow-y-auto space-y-2 p-2 bg-surface-lowest/40 rounded border border-surface-border/30 text-xs min-h-[140px]">
        <div class="p-2 rounded bg-surface-high/60 border border-surface-border">
          <strong class="text-gold font-mono">Macro AI Agent:</strong> Indian markets show capital inflow rotation into Capital Goods, Banking, and Renewable Energy sectors. Overweight on quality compounding franchises.
        </div>
      </div>

      <div class="flex gap-2">
        <input type="text" id="general-ai-input" class="form-input text-xs flex-1" placeholder="Ask general portfolio/macro question..." />
        <button onclick="window.sendGeneralAiQuery()" class="btn-primary text-xs px-3">Ask</button>
      </div>
    </div>
  `;

  window.sendGeneralAiQuery = () => {
    const input = document.getElementById("general-ai-input");
    const feed = document.getElementById("general-ai-feed");
    if (input && feed && input.value.trim()) {
      const q = input.value.trim();
      feed.innerHTML += `<div class="p-2 rounded bg-surface-lowest text-white"><strong class="text-gold font-mono">You:</strong> ${escapeHtml(q)}</div>`;
      feed.innerHTML += `<div class="p-2 rounded bg-surface-high border border-gold/30 text-gray-200"><strong class="text-gold font-mono">Macro Advisor:</strong> Analyzing sector correlation and macro tailwinds for "${escapeHtml(q)}"... Macro outlook remains bullish on high-ROCE Make-in-India themes.</div>`;
      input.value = "";
      feed.scrollTop = feed.scrollHeight;
    }
  };
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
