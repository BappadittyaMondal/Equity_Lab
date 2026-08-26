// growth_market_gap_panel.js – Growth vs Market Recognition Gap (E3) research view component
import { loadGrowthMarketGap } from "./api.js";

export async function renderGrowthMarketGapPanel(symbol = "RELIANCE") {
  const container = document.getElementById("growth-market-gap-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-4 bg-surface-high rounded w-1/3 mb-2"></div>
      <div class="h-12 bg-surface-high rounded mb-2"></div>
    </div>`;

  const data = await loadGrowthMarketGap(symbol);

  if (!data) {
    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border text-center text-muted text-xs">
        <span class="material-symbols-outlined text-gold">warning</span>
        <div>Growth-Market Gap data unavailable for ${symbol}</div>
      </div>`;
    return;
  }

  const gap = data.growth_recognition_gap != null ? data.growth_recognition_gap.toFixed(2) : "0.00";
  const classification = data.gap_classification || "N/A";
  const cagr = data.cagr_comparison || {};
  const fundamentalCagr = cagr.fundamental_cagr != null ? cagr.fundamental_cagr.toFixed(1) + "%" : "N/A";
  const priceCagr = cagr.price_cagr != null ? cagr.price_cagr.toFixed(1) + "%" : "N/A";

  const gapColor = parseFloat(gap) > 10 ? "text-green" : (parseFloat(gap) < -5 ? "text-red" : "text-gold");

  container.innerHTML = `
    <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-md">
      <div class="flex items-center justify-between mb-3 border-b border-surface-border/40 pb-2">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-gold text-sm">trending_up</span>
          <h4 class="text-sm font-bold text-white font-mono">Growth vs Market Recognition Gap (E3)</h4>
        </div>
        <span class="badge badge-neutral text-xs font-mono">${classification}</span>
      </div>
      <div class="grid grid-cols-3 gap-2 mb-2 font-mono text-center text-xs">
        <div class="p-2 bg-surface-low rounded">
          <div class="text-muted text-[10px]">Fundamental CAGR</div>
          <div class="font-bold text-white mt-0.5">${fundamentalCagr}</div>
        </div>
        <div class="p-2 bg-surface-low rounded">
          <div class="text-muted text-[10px]">Price CAGR</div>
          <div class="font-bold text-white mt-0.5">${priceCagr}</div>
        </div>
        <div class="p-2 bg-surface-low rounded">
          <div class="text-muted text-[10px]">Recognition Gap</div>
          <div class="font-bold ${gapColor} mt-0.5">${gap}%</div>
        </div>
      </div>
    </div>`;
}
