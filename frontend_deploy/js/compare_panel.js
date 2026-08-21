// compare_panel.js – Multi-Stock Comparison component
import { postStockCompare } from "./api.js";

export async function renderComparePanel(symbols = ["RELIANCE", "TCS", "INFY"]) {
  const container = document.getElementById("compare-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-32 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await postStockCompare(symbols);
  const items = (data && data.comparison) ? data.comparison : (Array.isArray(data) ? data : []);

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">compare_arrows</span>
        <h3 class="text-sm font-semibold text-white">Stock Comparison Engine</h3>
        <p class="text-xs mt-1">Select 2–5 tickers to compare fundamental scores, valuation multiples, and technical conviction calls.</p>
      </div>`;
    return;
  }

  const columns = items.map(c => `
    <div class="p-4 bg-surface-low rounded-lg border border-surface-border/40 space-y-3">
      <div class="flex items-center justify-between border-b border-surface-border/30 pb-2">
        <h4 class="font-mono font-bold text-base text-gold">${(c.symbol || "").replace(".NS", "")}</h4>
        <span class="badge badge-success">${c.verdict || "HOLD"}</span>
      </div>
      <div class="text-2xl font-mono font-bold text-white">${c.composite_score || 0} <span class="text-xs text-muted">/100</span></div>
      <div class="space-y-1.5 text-xs font-mono">
        <div class="flex justify-between text-muted"><span>Quality:</span> <strong class="text-white">${c.quality_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Growth:</span> <strong class="text-white">${c.growth_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Valuation:</span> <strong class="text-white">${c.valuation_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Momentum:</span> <strong class="text-white">${c.momentum_score || "—"}</strong></div>
      </div>
    </div>`).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">compare_arrows</span>
            Multi-Stock Fundamental & Technical Comparison
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Side-by-side Arbiter pillar metrics across selected equities</p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        ${columns}
      </div>
    </div>`;
}
