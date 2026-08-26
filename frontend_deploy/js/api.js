// api.js — Centralized API interaction layer for IERL frontend
// Handles health checks, data fetching, and chart rendering with authenticated API key injection.

const isLocalhost = typeof window !== 'undefined' && (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "" ||
  window.location.protocol === "file:"
);
const metaApiBase = typeof document !== 'undefined' ? document.querySelector('meta[name="ierl-api-base"]')?.getAttribute('content') : "";
const defaultProductionBackend = (typeof window !== 'undefined' && window.location.hostname.includes("vercel.app")) ? "https://equity-lab-c90s.onrender.com" : "";
const API_BASE = isLocalhost ? "" : (window.API_BASE || metaApiBase || defaultProductionBackend);

/**
 * Helper wrapper for fetch that automatically attaches the X-API-Key header.
 */
export async function apiFetch(endpoint, options = {}) {
  const apiKey = (typeof window !== 'undefined' && (window.__IERL_API_KEY || localStorage.getItem("ierl_api_key"))) || "";
  const headers = {
    ...(options.headers || {}),
  };
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;
  return await fetch(url, { ...options, headers });
}

/**
 * Check backend API health and display status in header.
 */
export async function initApiHealth() {
  try {
    const resp = await apiFetch(`/api/v1/health`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const indicator = document.getElementById("api-status");
    if (indicator) {
      indicator.textContent = `API: ${data.status || "ONLINE"} | v${data.version || "?"}`;
      indicator.classList.add("text-green");
    }
    // Store version for footer
    window.__IERL_API_VERSION = data.version || "unknown";
    window.__IERL_DATA_MODE = data.data_mode || "unknown";
  } catch (err) {
    const indicator = document.getElementById("api-status");
    if (indicator) {
      indicator.textContent = "API: OFFLINE";
      indicator.classList.add("text-red");
    }
    console.warn("IERL API health check failed:", err.message);
  }
}

/**
 * Load ticker strip quotes for the scrolling market tape.
 */
export async function loadTickerStrip() {
  const container = document.getElementById("ticker-strip");
  if (!container) return;

  let quotes = [];
  try {
    const resp = await apiFetch(`/api/v1/ticker-strip`);
    if (resp.ok) {
      quotes = await resp.json();
    }
  } catch (_) {}

  if (!Array.isArray(quotes) || quotes.length === 0) {
    container.innerHTML = `<span class="px-3 py-1 text-xs text-amber-400 font-mono">⚠️ MARKET TICKER DATA UNAVAILABLE</span>`;
    return;
  }

  const tickerHTML = quotes.map(q => {
    const sym = (q.symbol || "").replace(".NS", "").replace(".BO", "");
    const price = q.price != null ? `₹${q.price.toLocaleString("en-IN")}` : "—";
    const changePct = q.change_percent != null ? q.change_percent.toFixed(2) : "0.00";
    const changeColor = q.change_percent >= 0 ? "text-green" : "text-red";
    const arrow = q.change_percent >= 0 ? "▲" : "▼";
    return `
      <span class="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-mono whitespace-nowrap cursor-pointer hover:bg-gold/10 rounded" onclick="window.selectSymbol('${sym}')">
        <span class="font-bold text-gold">${sym}</span>
        <span class="text-white">${price}</span>
        <span class="${changeColor} font-semibold">${arrow} ${changePct}%</span>
      </span>`;
  }).join("");

  // Duplicate for seamless scroll animation
  container.innerHTML = `
    <div class="ticker-strip">${tickerHTML}${tickerHTML}</div>`;
}


/**
 * Load market regime data (VIX, Nifty level, regime classification).
 */
export async function loadRegimeData() {
  const container = document.getElementById("regime-panel");
  if (!container) return;

  try {
    const resp = await apiFetch(`/api/v1/regime`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    container.innerHTML = `
      <div class="flex items-center gap-4 text-xs font-mono">
        <span class="text-muted">Regime:</span>
        <span class="badge badge-${data.regime === 'volatile' ? 'danger' : data.regime === 'elevated' ? 'warning' : 'success'}">${(data.regime || "UNKNOWN").toUpperCase()}</span>
        ${data.vix != null ? `<span class="text-muted">VIX: <strong class="text-white">${data.vix}</strong></span>` : ""}
        ${data.nifty_spot != null ? `<span class="text-muted">Nifty: <strong class="text-white">${data.nifty_spot.toLocaleString("en-IN")}</strong></span>` : ""}
      </div>`;
  } catch (err) {
    container.innerHTML = `<span class="text-xs text-muted">Regime data unavailable</span>`;
    console.warn("Regime data load failed:", err.message);
  }
}

/**
 * Load available strategy modules catalog.
 */
export async function loadStrategyCatalog() {
  const container = document.getElementById("strategy-catalog");
  if (!container) return;

  try {
    const resp = await apiFetch(`/api/v1/strategies`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const strategies = data.strategies || data || [];

    if (!Array.isArray(strategies) || strategies.length === 0) {
      container.innerHTML = `<span class="text-xs text-muted">No strategies loaded</span>`;
      return;
    }

    const listHTML = strategies.map(s => `
      <div class="p-3 bg-surface-low rounded border border-surface-border/50 hover:border-gold/30 transition-colors">
        <div class="flex items-center justify-between mb-1">
          <span class="font-mono text-xs font-bold text-gold">${s.id || "?"}</span>
          <span class="badge ${s.status === 'production' ? 'badge-success' : 'badge-neutral'}">${s.status || "unknown"}</span>
        </div>
        <div class="text-sm font-semibold text-white">${s.name || "Unnamed Strategy"}</div>
        <div class="text-xs text-muted mt-0.5">${s.category || ""}</div>
      </div>`).join("");

    container.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        ${listHTML}
      </div>`;
  } catch (err) {
    container.innerHTML = `<span class="text-xs text-muted">Strategy catalog unavailable</span>`;
    console.warn("Strategy catalog load failed:", err.message);
  }
}

/**
 * Fetch historical OHLCV data and render a simple chart visualization.
 */
export async function fetchAndRenderChart(period = "1y") {
  const container = document.getElementById("chart-panel");
  if (!container) return;

  const symbol = window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  container.innerHTML = `
    <div class="p-4 bg-surface-lowest rounded-xl border animate-pulse">
      <div class="h-40 bg-surface-high rounded"></div>
    </div>`;

  try {
    const resp = await apiFetch(`/api/v1/ticker/${encodeURIComponent(symbol)}/history?period=${period}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const history = data.history || [];

    if (history.length === 0) {
      container.innerHTML = `
        <div class="p-4 bg-surface-lowest rounded-xl border text-center text-muted text-xs">
          No historical data available for ${data.symbol || symbol}
        </div>`;
      return;
    }

    // Simple SVG line chart
    const closes = history.map(d => d.close);
    const minPrice = Math.min(...closes);
    const maxPrice = Math.max(...closes);
    const range = maxPrice - minPrice || 1;
    const width = 600;
    const height = 160;

    const points = closes.map((c, i) => {
      const x = (i / (closes.length - 1)) * width;
      const y = height - ((c - minPrice) / range) * (height - 20) - 10;
      return `${x},${y}`;
    }).join(" ");

    const lastPrice = closes[closes.length - 1];
    const firstPrice = closes[0];
    const pctChange = ((lastPrice - firstPrice) / firstPrice * 100).toFixed(2);
    const lineColor = lastPrice >= firstPrice ? "var(--color-bullish-green)" : "var(--color-bearish-red)";

    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border">
        <div class="flex items-center justify-between mb-3">
          <div>
            <span class="font-mono text-sm font-bold text-gold">${(data.symbol || symbol).replace(".NS", "")}</span>
            <span class="text-xs text-muted ml-2">${period} chart</span>
          </div>
          <div class="text-xs font-mono">
            <span class="text-white">₹${lastPrice.toLocaleString("en-IN")}</span>
            <span class="${lastPrice >= firstPrice ? 'text-green' : 'text-red'} ml-1">(${pctChange}%)</span>
          </div>
        </div>
        <svg viewBox="0 0 ${width} ${height}" class="w-full" style="max-height: 180px;">
          <polyline fill="none" stroke="${lineColor}" stroke-width="2" points="${points}" />
        </svg>
        <div class="flex justify-between text-xs text-muted mt-1 font-mono">
          <span>${history[0].date}</span>
          <span>${history[history.length - 1].date}</span>
        </div>
      </div>`;
  } catch (err) {
    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border text-center text-xs text-muted">
        Chart data unavailable: ${err.message}
      </div>`;
    console.warn("Chart load failed:", err.message);
  }
}

/**
 * Load watchlist data.
 */
export async function loadWatchlist() {
  try {
    const resp = await apiFetch(`/api/v1/watchlist`);
    if (resp.ok) {
      const data = await resp.json();
      window.__IERL_WATCHLIST = data.items || data || [];
    }
  } catch (_) {}
}

/**
 * Fetch unified scorecard research data for a symbol.
 */
export async function loadScorecard(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/scorecard?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Scorecard load failed:", err.message);
    return null;
  }
}

/**
 * Fetch CAGR sensitivity matrix projections for a symbol.
 */
export async function loadCAGRMatrix(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/cagr-matrix?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("CAGR Matrix load failed:", err.message);
    return null;
  }
}

/**
 * Fetch active swing trade alert setups.
 */
export async function loadSwingAlerts() {
  try {
    const resp = await apiFetch(`/api/v1/strategies/swing-alerts`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Swing alerts load failed:", err.message);
    return null;
  }
}

/**
 * Fetch system model drift and performance health.
 */
export async function loadDriftStatus() {
  try {
    const resp = await apiFetch(`/api/v1/monitoring/drift`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Drift status load failed:", err.message);
    return null;
  }
}

/**
 * Fetch multibagger screening candidates across Indian equity universe.
 */
export async function loadMultibaggerScreener(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const url = `/api/v1/research/multibagger-screener${query ? `?${query}` : ''}`;
    const resp = await apiFetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Multibagger screener load failed:", err.message);
    return null;
  }
}

/**
 * Estimate return probability for a composite score and target horizon.
 */
export async function fetchReturnProbability(compositeScore = 75, horizonMonths = 12) {
  try {
    const resp = await apiFetch(`/api/v1/return-probability`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ composite_score: compositeScore, horizon_months: horizonMonths })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Return probability fetch failed:", err.message);
    return null;
  }
}

/**
 * Fetch underlying research thesis record for a symbol.
 */
export async function loadThesisRecord(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/data/thesis/${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Thesis record load failed:", err.message);
    return null;
  }
}

/**
 * Fetch business lifecycle stage for a symbol.
 */
export async function loadLifecycleStage(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/data/lifecycle/${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Lifecycle stage load failed:", err.message);
    return null;
  }
}

/**
 * Compare multiple equities across valuation, growth, quality, and momentum metrics.
 */
export async function postStockCompare(symbols = ["RELIANCE", "TCS"]) {
  try {
    const resp = await apiFetch(`/api/v1/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbols })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Stock comparison failed:", err.message);
    return null;
  }
}

/**
 * Fetch company timeline and milestone events for a symbol.
 */
export async function loadCompanyTimeline(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/data/companies/${sym}/timeline`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Company timeline load failed:", err.message);
    return null;
  }
}

/**
 * Fetch governance quality analysis for a symbol.
 */
export async function loadGovernanceQuality(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/governance-quality?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Governance quality load failed:", err.message);
    return null;
  }
}

/**
 * Fetch growth arbitrage analysis for a symbol.
 */
export async function loadGrowthArbitrage(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/growth-arbitrage?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Growth arbitrage load failed:", err.message);
    return null;
  }
}

/**
 * Fetch growth inflection points for a symbol.
 */
export async function loadGrowthInflection(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/growth-inflection?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Growth inflection load failed:", err.message);
    return null;
  }
}

/**
 * Fetch growth vs market recognition gap analysis for a symbol.
 */
export async function loadGrowthMarketGap(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/growth-market-gap?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Growth market gap load failed:", err.message);
    return null;
  }
}
export const fetchGrowthMarketGap = loadGrowthMarketGap;

/**
 * Fetch turnaround stage classification for a symbol.
 */
export async function loadTurnaroundStage(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/research/turnaround-stage?symbol=${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Turnaround stage load failed:", err.message);
    return null;
  }
}

/**
 * Fetch portfolio holdings summary.
 */
export async function loadPortfolioHoldings() {
  try {
    const resp = await apiFetch(`/api/v1/portfolio/`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Portfolio holdings load failed:", err.message);
    return null;
  }
}

/**
 * Fetch portfolio investment narrative for a symbol.
 */
export async function loadPortfolioNarrative(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/portfolio/narrate/${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Portfolio narrative load failed:", err.message);
    return null;
  }
}

/**
 * Fetch detailed ticker metadata for a symbol.
 */
export async function loadTickerDetail(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/ticker/${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Ticker detail load failed:", err.message);
    return null;
  }
}

/**
 * Fetch historical OHLCV series for a ticker symbol.
 */
export async function loadTickerHistory(symbol = "RELIANCE", period = "1y") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/ticker/${sym}/history?period=${period}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Ticker history load failed:", err.message);
    return null;
  }
}

/**
 * Simulate options payoff matrix for a symbol.
 */
export async function postOptionsPayoff(symbol = "RELIANCE", spotPrice = 2500, strikePrice = 2500) {
  try {
    const resp = await apiFetch(`/api/v1/options/a2-payoff`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, spot_price: spotPrice, strike_price: strikePrice })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Options payoff calculation failed:", err.message);
    return null;
  }
}

/**
 * Fetch strategy engine health indicators.
 */
export async function loadStrategyHealth() {
  try {
    const resp = await apiFetch(`/api/v1/monitoring/strategy-health`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Strategy health load failed:", err.message);
    return null;
  }
}

/**
 * Fetch prediction ledger audit logs.
 */
export async function loadPredictionLedger() {
  try {
    const resp = await apiFetch(`/api/v1/monitoring/prediction-ledger`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("Prediction ledger load failed:", err.message);
    return null;
  }
}

/**
 * Fetch system operational readiness status.
 */
export async function loadSystemReadiness() {
  try {
    const resp = await apiFetch(`/api/v1/readiness`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("System readiness load failed:", err.message);
    return null;
  }
}

/**
 * Fetch system data alerts.
 */
export async function loadSystemDataAlerts() {
  try {
    const resp = await apiFetch(`/api/v1/data/alerts`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("System data alerts load failed:", err.message);
    return null;
  }
}

/**
 * Fetch 100-Point MIVS Scorecard for a symbol.
 */
export async function loadMIVSScore(symbol = "RELIANCE") {
  try {
    const sym = encodeURIComponent(symbol);
    const resp = await apiFetch(`/api/v1/multibagger/mivs/${sym}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (err) {
    console.warn("MIVS score load failed:", err.message);
    return null;
  }
}

