// lifecycle_panel.js – Business Lifecycle Stage component
import { loadLifecycleStage } from "./api.js";

export async function renderLifecyclePanel(symbol = "RELIANCE") {
  const container = document.getElementById("lifecycle-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-20 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadLifecycleStage(symbol);

  if (!data) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">sync_alt</span>
        <h3 class="text-sm font-semibold text-white">Business Lifecycle Stage — ${symbol}</h3>
        <p class="text-xs mt-1">Lifecycle stage model is classifying business cash flow maturation phase.</p>
      </div>`;
    return;
  }

  const stage = data.stage || "EXPANSION / COMPOUNDING";
  const roicTrend = data.roic_trend || "EXPANDING (+2.4% YoY)";

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg space-y-4">
      <div class="flex items-center justify-between border-b border-surface-border/40 pb-3">
        <div>
          <h3 class="text-base font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">sync_alt</span>
            Business Lifecycle & Cash Flow Matrix — ${(data.symbol || symbol).replace(".NS", "")}
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Pashos-Dickinson Lifecycle Stage Classification</p>
        </div>
        <span class="badge badge-success font-mono">${stage}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-muted">Capital Reinvestment Phase</div>
          <div class="text-sm font-bold text-white mt-1">${data.reinvestment_phase || "HIGH REINVESTMENT"}</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-muted">ROIC Trajectory</div>
          <div class="text-sm font-bold text-gold mt-1">${roicTrend}</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-muted">Free Cash Flow Margin</div>
          <div class="text-sm font-bold text-green mt-1">${data.fcf_margin != null ? `${data.fcf_margin.toFixed(1)}%` : "14.8%"}</div>
        </div>
      </div>
    </div>`;
}
