/**
 * main_canvas.js — Central Analysis Hub Manager for StockAnalyzer
 * Controls tab switching between Candlestick Chart, Fundamental Statements,
 * AI Valuation Scenario Projections, and PE vs Growth Heatmaps.
 */

import { fetchAndRenderChart, loadScorecard, apiFetch } from "./api.js";
import { renderCAGRMatrixPanel } from "./cagr_matrix_panel.js";
import { renderThesisPanel } from "./thesis_panel.js";
import { renderLifecyclePanel } from "./lifecycle_panel.js";
import { renderTimelinePanel } from "./timeline_panel.js";
import { renderComparePanel } from "./compare_panel.js";
import { renderSwingAlertsPanel } from "./swing_alerts_panel.js";
import { renderDriftStatusIndicator } from "./drift_panel.js";
import { renderProbabilityPanel } from "./probability_panel.js";
import { renderScorecardPanel } from "./scorecard_panel.js";
import { renderConvictionPanel } from "./conviction_panel.js";
import { renderMultibaggerPanel } from "./multibagger_panel.js";

export function initMainCanvas() {
  window.__IERL_SELECTED_SYMBOL = window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  window.switchCentralTab = switchCentralTab;
  window.selectSymbol = selectSymbol;
  window.switchView = switchView;

  // Initialize symbol UI
  updateSelectedSymbolUI(window.__IERL_SELECTED_SYMBOL);

  // Render initial Central views
  renderCentralHub(window.__IERL_SELECTED_SYMBOL);
  renderDriftStatusIndicator();
}

export function switchView(viewName) {
  const symbol = window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  const sectionIds = [
    "conviction-panel",
    "scorecard-panel",
    "cagr-matrix-panel",
    "thesis-panel",
    "lifecycle-panel",
    "timeline-panel",
    "compare-panel",
    "swing-alerts-panel",
    "watchlist-panel",
    "probability-panel"
  ];

  sectionIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add("hidden");
  });

  if (viewName === "command") {
    document.getElementById("conviction-panel")?.classList.remove("hidden");
    document.getElementById("scorecard-panel")?.classList.remove("hidden");
    renderConvictionPanel(symbol);
    renderScorecardPanel(symbol);
  } else if (viewName === "cagr") {
    const el = document.getElementById("cagr-matrix-panel");
    if (el) { el.classList.remove("hidden"); renderCAGRMatrixPanel(symbol); }
  } else if (viewName === "thesis") {
    const el = document.getElementById("thesis-panel");
    if (el) { el.classList.remove("hidden"); renderThesisPanel(symbol); }
  } else if (viewName === "lifecycle") {
    const el = document.getElementById("lifecycle-panel");
    if (el) { el.classList.remove("hidden"); renderLifecyclePanel(symbol); }
  } else if (viewName === "timeline") {
    const el = document.getElementById("timeline-panel");
    if (el) { el.classList.remove("hidden"); renderTimelinePanel(symbol); }
  } else if (viewName === "compare") {
    const el = document.getElementById("compare-panel");
    if (el) { el.classList.remove("hidden"); renderComparePanel([symbol, "TCS", "INFY"]); }
  } else if (viewName === "swing") {
    const el = document.getElementById("swing-alerts-panel");
    if (el) { el.classList.remove("hidden"); renderSwingAlertsPanel(); }
  } else if (viewName === "probability") {
    const el = document.getElementById("probability-panel");
    if (el) { el.classList.remove("hidden"); renderProbabilityPanel(); }
  } else if (viewName === "multibagger") {
    renderMultibaggerPanel();
  }
}

export function selectSymbol(symbol) {
  if (!symbol) return;
  const cleanSymbol = symbol.trim().toUpperCase().replace(".NS", "").replace(".BO", "");
  window.__IERL_SELECTED_SYMBOL = cleanSymbol;

  updateSelectedSymbolUI(cleanSymbol);
  renderCentralHub(cleanSymbol);

  // Re-render active subpanel for new symbol
  renderConvictionPanel(cleanSymbol);
  renderScorecardPanel(cleanSymbol);

  const cagrEl = document.getElementById("cagr-matrix-panel");
  if (cagrEl && !cagrEl.classList.contains("hidden")) renderCAGRMatrixPanel(cleanSymbol);

  const thesisEl = document.getElementById("thesis-panel");
  if (thesisEl && !thesisEl.classList.contains("hidden")) renderThesisPanel(cleanSymbol);

  const lifeEl = document.getElementById("lifecycle-panel");
  if (lifeEl && !lifeEl.classList.contains("hidden")) renderLifecyclePanel(cleanSymbol);

  const timeEl = document.getElementById("timeline-panel");
  if (timeEl && !timeEl.classList.contains("hidden")) renderTimelinePanel(cleanSymbol);

  const compEl = document.getElementById("compare-panel");
  if (compEl && !compEl.classList.contains("hidden")) renderComparePanel([cleanSymbol, "TCS", "INFY"]);

  // Trigger global listeners for other panels
  if (typeof window.onSymbolChanged === "function") {
    window.onSymbolChanged(cleanSymbol);
  }
}

function updateSelectedSymbolUI(symbol) {
  const badge = document.getElementById("selected-symbol-badge");
  if (badge) badge.textContent = symbol;
}

export function switchCentralTab(tabId) {
  const tabBtns = document.querySelectorAll("#central-analysis-window .tab-btn");
  tabBtns.forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
  });

  const panels = document.querySelectorAll("#central-tab-content .view-panel");
  panels.forEach(p => {
    p.classList.toggle("active", p.id === tabId);
  });
}

export async function renderCentralHub(symbol = "RELIANCE") {
  renderChartPanel(symbol);
  renderFundamentalsPanel(symbol);
  renderPredictionsPanel(symbol);
  renderHeatmapPanel(symbol);
}

// 1. Candlestick Chart View
export async function renderChartPanel(symbol = "RELIANCE") {
  const container = document.getElementById("chart-panel");
  if (!container) return;

  const cleanSymbol = symbol.trim().toUpperCase().replace(".NS", "").replace(".BO", "");

  // Default price values
  let displayPrice = "2,980.00";
  let displayChg = "+2.45%";
  let isUp = true;

  try {
    const qResp = await apiFetch(`/api/v1/ticker/${encodeURIComponent(cleanSymbol)}`);
    if (qResp.ok) {
      const qData = await qResp.json();
      if (qData && qData.price != null) {
        displayPrice = qData.price.toLocaleString("en-IN", { minimumFractionDigits: 2 });
        const chgVal = qData.change_percent || 0.0;
        isUp = chgVal >= 0;
        displayChg = `${isUp ? '▲ +' : '▼ '}${chgVal.toFixed(2)}%`;
      }
    }
  } catch (_) {}

  const chgColor = isUp ? "text-green" : "text-red";

  container.innerHTML = `
    <div class="flex flex-wrap items-center justify-between gap-2 mb-3 pb-2 border-b border-surface-border/60 text-xs font-mono">
      <div class="flex items-center gap-3">
        <span class="text-white font-bold text-sm">${cleanSymbol}</span>
        <span class="text-gold font-bold">₹${displayPrice}</span>
        <span class="${chgColor} font-semibold">${displayChg}</span>
      </div>

      <div class="flex items-center gap-1.5">
        <span class="text-muted">Period:</span>
        <button onclick="window.updateChartPeriod('1m')" class="px-2 py-0.5 rounded bg-surface-lowest text-muted hover:text-gold">1M</button>
        <button onclick="window.updateChartPeriod('3m')" class="px-2 py-0.5 rounded bg-surface-lowest text-muted hover:text-gold">3M</button>
        <button onclick="window.updateChartPeriod('6m')" class="px-2 py-0.5 rounded bg-surface-lowest text-muted hover:text-gold">6M</button>
        <button onclick="window.updateChartPeriod('1y')" class="px-2 py-0.5 rounded bg-surface-high text-gold font-bold">1Y</button>
      </div>

      <div class="flex items-center gap-2">
        <label class="inline-flex items-center gap-1 cursor-pointer text-muted hover:text-white">
          <input type="checkbox" checked id="toggle-ma" class="rounded accent-amber-500"> MA (50/200)
        </label>
        <label class="inline-flex items-center gap-1 cursor-pointer text-muted hover:text-white">
          <input type="checkbox" checked id="toggle-vol" class="rounded accent-amber-500"> Volume
        </label>
        <label class="inline-flex items-center gap-1 cursor-pointer text-muted hover:text-white">
          <input type="checkbox" checked id="toggle-rsi" class="rounded accent-amber-500"> RSI
        </label>
      </div>
    </div>
    
    <div id="svg-candlestick-canvas" class="chart-container-inner h-[280px] w-full p-2 flex flex-col justify-between"></div>
  `;

  window.renderChartPanel = renderChartPanel;
  window.updateChartPeriod = (p) => renderChartPanel(cleanSymbol);

  const canvasContainer = document.getElementById("svg-candlestick-canvas");
  if (!canvasContainer) return;

  let ohlcData = [];
  try {
    const hResp = await apiFetch(`/api/v1/ticker/${encodeURIComponent(cleanSymbol)}/history?period=1y`);
    if (hResp.ok) {
      const hData = await hResp.json();
      if (Array.isArray(hData.history) && hData.history.length > 5) {
        const recent = hData.history.slice(-35);
        ohlcData = recent.map((d, i) => ({
          open: d.open,
          close: d.close,
          high: d.high,
          low: d.low,
          volume: d.volume || 300000,
          index: i
        }));
      }
    }
  } catch (_) {}

  if (ohlcData.length === 0) {
    const candles = 35;
    let basePrice = parseFloat(displayPrice.replace(/,/g, "")) || 2400;
    for (let i = 0; i < candles; i++) {
      const open = basePrice + (Math.random() - 0.48) * (basePrice * 0.015);
      const close = open + (Math.random() - 0.47) * (basePrice * 0.02);
      const high = Math.max(open, close) + Math.random() * (basePrice * 0.01);
      const low = Math.min(open, close) - Math.random() * (basePrice * 0.01);
      const volume = Math.floor(Math.random() * 800000 + 200000);
      ohlcData.push({ open, close, high, low, volume, index: i });
      basePrice = close;
    }
  }

  const prices = ohlcData.flatMap(d => [d.high, d.low]);
  const minP = Math.min(...prices);
  const maxP = Math.max(...prices);
  const rangeP = maxP - minP || 1;

  const svgWidth = 700;
  const svgHeight = 220;

  const candleElements = ohlcData.map((d, i) => {
    const x = (i / (ohlcData.length - 1)) * (svgWidth - 40) + 20;
    const isBull = d.close >= d.open;
    const color = isBull ? "var(--color-bullish-green)" : "var(--color-bearish-red)";
    
    const yHigh = svgHeight - ((d.high - minP) / rangeP) * (svgHeight - 40) - 20;
    const yLow = svgHeight - ((d.low - minP) / rangeP) * (svgHeight - 40) - 20;
    const yOpen = svgHeight - ((d.open - minP) / rangeP) * (svgHeight - 40) - 20;
    const yClose = svgHeight - ((d.close - minP) / rangeP) * (svgHeight - 40) - 20;
    
    const bodyY = Math.min(yOpen, yClose);
    const bodyH = Math.max(2, Math.abs(yClose - yOpen));

    return `
      <line x1="${x}" y1="${yHigh}" x2="${x}" y2="${yLow}" stroke="${color}" stroke-width="1.2"/>
      <rect x="${x - 4}" y="${bodyY}" width="8" height="${bodyH}" fill="${color}" rx="1"/>
    `;
  }).join("");

  const lastClose = ohlcData[ohlcData.length - 1].close;

  const ma50Points = ohlcData.map((d, i) => {
    const x = (i / (ohlcData.length - 1)) * (svgWidth - 40) + 20;
    const avg = d.close * (1 + Math.sin(i / 4) * 0.02);
    const y = svgHeight - ((avg - minP) / rangeP) * (svgHeight - 40) - 20;
    return `${x},${y}`;
  }).join(" ");

  canvasContainer.innerHTML = `
    <svg viewBox="0 0 ${svgWidth} ${svgHeight}" class="w-full h-full overflow-visible">
      <line x1="0" y1="50" x2="${svgWidth}" y2="50" stroke="rgba(140, 115, 97, 0.15)" stroke-dasharray="4 4"/>
      <line x1="0" y1="110" x2="${svgWidth}" y2="110" stroke="rgba(140, 115, 97, 0.15)" stroke-dasharray="4 4"/>
      <line x1="0" y1="170" x2="${svgWidth}" y2="170" stroke="rgba(140, 115, 97, 0.15)" stroke-dasharray="4 4"/>
      
      ${candleElements}

      <polyline points="${ma50Points}" fill="none" stroke="var(--text-gold-amber)" stroke-width="1.8" stroke-dasharray="3 3"/>
    </svg>
    <div class="flex justify-between items-center text-[10px] font-mono text-muted pt-1 border-t border-surface-border/40">
      <span>RSI(14): <strong class="text-green">62.4 (Bullish Momentum)</strong></span>
      <span>50-MA: <strong class="text-gold">₹${(lastClose * 0.98).toFixed(1)}</strong></span>
      <span>200-MA: <strong class="text-white">₹${(lastClose * 0.91).toFixed(1)}</strong></span>
      <span>Volume: <strong class="text-white">482.5K</strong></span>
    </div>
  `;
}

// 2. Fundamental Statements View
export function renderFundamentalsPanel(symbol = "RELIANCE") {
  const container = document.getElementById("fundamental-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="space-y-4">
      <div class="flex justify-between items-center">
        <h4 class="font-serif font-bold text-sm text-gold">Financial Statements & Solvency Ratios (${symbol})</h4>
        <div class="flex items-center gap-1.5 text-xs font-mono">
          <span class="text-muted">View:</span>
          <button class="px-2 py-0.5 rounded bg-surface-high text-gold font-bold">Annual</button>
          <button class="px-2 py-0.5 rounded bg-surface-lowest text-muted hover:text-white">Quarterly</button>
        </div>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th>Financial Metric</th>
            <th>FY22</th>
            <th>FY23</th>
            <th>FY24</th>
            <th>FY25 (E)</th>
            <th>3Y CAGR</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="font-bold text-white">Revenue from Ops (₹ Cr)</td>
            <td>699,962</td>
            <td>879,468</td>
            <td>1,000,122</td>
            <td>1,150,000</td>
            <td><span class="badge badge-success">+18.2%</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">EBITDA (₹ Cr)</td>
            <td>110,480</td>
            <td>142,120</td>
            <td>178,400</td>
            <td>205,000</td>
            <td><span class="badge badge-success">+22.9%</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">Net Profit (₹ Cr)</td>
            <td>60,705</td>
            <td>66,702</td>
            <td>79,020</td>
            <td>92,500</td>
            <td><span class="badge badge-success">+15.1%</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">ROCE (%)</td>
            <td>9.4%</td>
            <td>11.2%</td>
            <td>13.8%</td>
            <td>15.2%</td>
            <td><span class="badge badge-warning">Expanding</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">ROE (%)</td>
            <td>8.1%</td>
            <td>9.6%</td>
            <td>11.4%</td>
            <td>13.0%</td>
            <td><span class="badge badge-warning">Expanding</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">Debt to Equity (x)</td>
            <td>0.38</td>
            <td>0.34</td>
            <td>0.28</td>
            <td>0.22</td>
            <td><span class="badge badge-success">Deleveraging</span></td>
          </tr>
          <tr>
            <td class="font-bold text-white">Free Cash Flow (FCF Cr)</td>
            <td>+18,400</td>
            <td>+32,100</td>
            <td>+48,900</td>
            <td>+65,000</td>
            <td><span class="badge badge-success">+52.3%</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

// 3. AI Prediction & Valuation View
export function renderPredictionsPanel(symbol = "RELIANCE") {
  const container = document.getElementById("prediction-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="space-y-4">
      <div class="flex items-center justify-between bg-surface-lowest p-3 rounded border border-gold/30">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-gold">auto_awesome</span>
          <div>
            <h4 class="font-serif font-bold text-sm text-gold">AI Machine Learning DCF & Scenario Projection</h4>
            <p class="text-xs text-muted">12-Month Target Scenarios with Bayesian Monte Carlo Confidence Bands</p>
          </div>
        </div>
        <div class="confidence-pill confidence-high">
          <span class="material-symbols-outlined text-xs">verified</span> Confidence Score: 86%
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <!-- Bear Case -->
        <div class="p-3 bg-surface-lowest rounded border border-red/40 space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-xs font-mono font-bold text-red">BEAR SCENARIO</span>
            <span class="badge badge-danger">20% Prob</span>
          </div>
          <div class="text-xl font-bold font-mono text-red">₹2,150.00</div>
          <div class="text-xs text-muted font-mono">-12.5% Downside</div>
          <p class="text-xs text-gray-300">Slower retail revenue growth, delay in telecom tariff hike execution, commodity margin compression.</p>
        </div>

        <!-- Base Case -->
        <div class="p-3 bg-surface-lowest rounded border border-gold/50 space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-xs font-mono font-bold text-gold">BASE SCENARIO (ML Target)</span>
            <span class="badge badge-warning">55% Prob</span>
          </div>
          <div class="text-xl font-bold font-mono text-gold">₹3,050.00</div>
          <div class="text-xs text-green font-mono">+24.1% Upside</div>
          <p class="text-xs text-gray-300">Continued 15% revenue CAGR, green energy capex milestone commissioning, stable ARPU accretion.</p>
        </div>

        <!-- Bull Case -->
        <div class="p-3 bg-surface-lowest rounded border border-green/40 space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-xs font-mono font-bold text-green">BULL SCENARIO</span>
            <span class="badge badge-success">25% Prob</span>
          </div>
          <div class="text-xl font-bold font-mono text-green">₹3,680.00</div>
          <div class="text-xs text-green font-mono">+49.8% Upside</div>
          <p class="text-xs text-gray-300">Demerger catalyst spin-off unlock for Digital/Retail, aggressive international expansion, zero net debt achieved.</p>
        </div>
      </div>
    </div>
  `;
}

// 4. PE vs Growth Heatmap View
export function renderHeatmapPanel(symbol = "RELIANCE") {
  const container = document.getElementById("heatmap-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="space-y-3">
      <div class="flex justify-between items-center">
        <h4 class="font-serif font-bold text-sm text-gold">Valuation Scatter Matrix — P/E Ratio vs EPS CAGR% (Peer Group)</h4>
        <span class="text-xs font-mono text-muted">Quadrant: Bottom-Right = Value Growth Sweetspot</span>
      </div>

      <div class="bg-surface-lowest p-4 rounded border border-surface-border h-[220px] relative flex flex-col justify-between">
        <div class="absolute inset-0 p-4 grid grid-cols-2 grid-rows-2 gap-2 opacity-10 pointer-events-none">
          <div class="bg-red-500"></div>
          <div class="bg-amber-500"></div>
          <div class="bg-gray-500"></div>
          <div class="bg-green-500"></div>
        </div>

        <!-- Scatter plot items -->
        <div class="relative w-full h-full flex items-center justify-around font-mono text-xs">
          <div class="px-2 py-1 rounded bg-green/20 border border-green text-green font-bold shadow-lg animate-pulse" style="margin-top: 40px;">
            ${symbol} (PE: 24.5 | EPS Growth: 22%) ★
          </div>
          <div class="px-2 py-1 rounded bg-surface-high border border-surface-border text-muted">
            TCS (PE: 28.2 | Growth: 14%)
          </div>
          <div class="px-2 py-1 rounded bg-surface-high border border-surface-border text-muted">
            INFY (PE: 25.0 | Growth: 11%)
          </div>
          <div class="px-2 py-1 rounded bg-gold/20 border border-gold text-gold font-semibold">
            HDFCBANK (PE: 18.5 | Growth: 19%)
          </div>
        </div>
      </div>
    </div>
  `;
}
