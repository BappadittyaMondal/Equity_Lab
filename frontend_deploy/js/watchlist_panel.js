// watchlist_panel.js – Renders watchlist with conviction drift indicators & digest API
import { renderConvictionPanel } from "./conviction_panel.js";

const API_BASE = window.API_BASE || "";

export async function renderWatchlistPanel() {
  const container = document.getElementById('watchlist-panel');
  if (!container) return;

  // 1. Loading State (Skeleton)
  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border animate-pulse">
      <div class="h-5 bg-surface-high rounded w-1/4 mb-3"></div>
      <div class="h-20 bg-surface-high rounded"></div>
    </div>`;

  try {
    let items = [];
    let generatedAt = null;
    let isDigest = false;

    // Try fetching nightly digest first
    try {
      const digestResp = await fetch(`${API_BASE}/api/v1/digest/watchlist`);
      if (digestResp.ok) {
        const digestData = await digestResp.json();
        generatedAt = digestData.generated_at;
        const rawData = digestData.data || digestData.items || {};
        if (Array.isArray(rawData)) {
          items = rawData;
        } else if (typeof rawData === 'object') {
          items = Object.values(rawData);
        }
        isDigest = true;
      }
    } catch (_) {
      // Fallback to watchlist CRUD endpoint
    }

    if (!items.length) {
      const resp = await fetch(`${API_BASE}/api/v1/watchlist`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      items = data.items || data || [];
    }

    // 2. Empty State
    if (!items || !items.length) {
      container.innerHTML = `
        <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
          <span class="material-symbols-outlined text-3xl mb-1 text-gold">bookmark_border</span>
          <h3 class="text-sm font-semibold text-gold">Watchlist is Empty</h3>
          <p class="text-xs">No equities currently monitored for conviction drift.</p>
        </div>`;
      return;
    }

    // Build Rows
    const rowsHTML = items.map(item => {
      const sym = item.symbol || "N/A";
      const score = item.conviction_score !== undefined ? item.conviction_score : 50;
      const verdict = item.verdict || "NEUTRAL";
      const delta = item.delta || 0;

      let trendSymbol = "■";
      let trendColor = "text-gray-400";
      if (delta > 0 || score >= 70) {
        trendSymbol = "▲";
        trendColor = "text-green-400";
      } else if (delta < 0 || score <= 40) {
        trendSymbol = "▼";
        trendColor = "text-red-400";
      }

      let verdictBadge = "bg-gray-800 text-gray-300";
      if (verdict === "Strong Buy" || verdict === "Buy" || verdict === "Accumulate") verdictBadge = "bg-green-900/60 text-green-300 border-green-700/50";
      if (verdict === "Avoid") verdictBadge = "bg-red-900/60 text-red-300 border-red-700/50";

      return `
        <tr class="hover:bg-surface-high/60 cursor-pointer transition-colors border-b border-surface-border/50"
            onclick="window.selectWatchlistSymbol('${sym}')">
          <td class="py-2.5 px-3 font-mono font-bold text-gold">${sym}</td>
          <td class="py-2.5 px-3">
            <span class="px-2 py-0.5 text-xs font-mono rounded border ${verdictBadge}">
              ${verdict}
            </span>
          </td>
          <td class="py-2.5 px-3 font-mono font-semibold text-white text-right">${score}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold ${trendColor}">
            ${trendSymbol} <span class="text-xs text-muted font-normal">(${delta >= 0 ? '+' : ''}${delta})</span>
          </td>
        </tr>`;
    }).join('');

    const digestInfo = isDigest ? `
      <span class="text-xs text-muted">Nightly Scan Digest: <strong class="text-gold font-mono">${generatedAt ? generatedAt.substring(0, 16).replace('T', ' ') : 'Active'}</strong></span>` : '';

    const panelHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border">
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="text-lg font-bold text-gold tracking-tight">Watchlist — Conviction & Thesis Drift</h3>
            ${digestInfo}
          </div>
          <button class="px-2.5 py-1 text-xs font-mono bg-surface-low hover:bg-surface-high text-gold rounded border"
                  onclick="renderWatchlistPanel()">
            Refresh
          </button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="text-muted border-b border-surface-border text-xs uppercase font-mono">
                <th class="py-2 px-3">Symbol</th>
                <th class="py-2 px-3">Verdict</th>
                <th class="py-2 px-3 text-right">Conviction Score</th>
                <th class="py-2 px-3 text-right">Drift Trend</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHTML}
            </tbody>
          </table>
        </div>
      </div>`;

    container.innerHTML = panelHTML;

    // Attach global window handler for row clicks
    window.selectWatchlistSymbol = (symbol) => {
      renderConvictionPanel(symbol);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

  } catch (err) {
    // 3. Error State
    container.innerHTML = `
      <div class="p-6 bg-red-950/80 border border-red-600/60 rounded-xl text-red-200">
        <div class="flex items-center gap-2 mb-2 font-bold">
          <span class="material-symbols-outlined">warning</span>
          <span>Failed to load Watchlist Digest</span>
        </div>
        <p class="text-xs text-red-300 mb-3">${err.message || 'Error fetching watchlist.'}</p>
        <button class="px-3 py-1 bg-red-800 hover:bg-red-700 text-white font-mono text-xs rounded border"
                onclick="renderWatchlistPanel()">
          Retry
        </button>
      </div>`;
  }
}
