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

  const columns = (items && items.length > 0) ? items.map(c => `
    <div class="p-4 bg-surface-low rounded-lg border border-surface-border/40 space-y-3">
      <div class="flex items-center justify-between border-b border-surface-border/30 pb-2">
        <h4 class="font-mono font-bold text-base text-gold cursor-pointer hover:underline" onclick="window.selectSymbol('${c.symbol}')">${(c.symbol || "").replace(".NS", "")}</h4>
        <span class="px-2 py-0.5 text-xs font-mono rounded border ${c.verdict === 'Buy' || c.verdict === 'Strong Buy' ? 'bg-green-900/60 text-green-300 border-green-700/50' : 'bg-surface-high text-gold border-surface-border'}">${c.verdict || "HOLD"}</span>
      </div>
      <div class="text-2xl font-mono font-bold text-white">${c.composite_score || 0} <span class="text-xs text-muted">/100</span></div>
      <div class="space-y-1.5 text-xs font-mono">
        <div class="flex justify-between text-muted"><span>Quality:</span> <strong class="text-white">${c.quality_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Growth:</span> <strong class="text-white">${c.growth_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Valuation:</span> <strong class="text-white">${c.valuation_score || "—"}</strong></div>
        <div class="flex justify-between text-muted"><span>Momentum:</span> <strong class="text-white">${c.momentum_score || "—"}</strong></div>
      </div>
    </div>`).join("") : `<div class="col-span-3 text-center text-xs text-muted p-4">No comparison metrics available for selected symbols.</div>`;

  const currentSymStr = symbols.join(", ");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <h3 class="text-lg font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">compare_arrows</span>
            Multi-Stock Fundamental & Technical Comparison
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Side-by-side Arbiter pillar metrics across selected equities</p>
        </div>
        
        <div class="flex items-center gap-2">
          <input type="text" id="compare-symbols-input" value="${currentSymStr}" placeholder="e.g. RELIANCE, TCS, INFY" 
                 class="px-3 py-1.5 text-xs font-mono bg-surface-low text-white rounded border border-surface-border focus:border-gold outline-none w-56">
          <button id="compare-btn" class="px-3 py-1.5 text-xs font-mono bg-gold/20 hover:bg-gold/30 text-gold rounded border border-gold/40 transition-colors">
            Compare
          </button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        ${columns}
      </div>
    </div>`;

  // Attach click handler to Compare button
  const compareBtn = document.getElementById("compare-btn");
  const compareInput = document.getElementById("compare-symbols-input");

  if (compareBtn && compareInput) {
    compareBtn.addEventListener("click", () => {
      const raw = compareInput.value;
      const parsed = raw.split(",").map(s => s.trim().toUpperCase()).filter(Boolean);
      if (parsed.length > 0) {
        renderComparePanel(parsed);
      }
    });
  }
}

// Expose globally
window.renderComparePanel = renderComparePanel;
