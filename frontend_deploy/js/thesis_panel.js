// thesis_panel.js – Research Investment Thesis & Conviction Rationale component
import { loadThesisRecord } from "./api.js";

export async function renderThesisPanel(symbol = "RELIANCE") {
  const container = document.getElementById("thesis-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-20 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadThesisRecord(symbol);

  if (!data) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">article</span>
        <h3 class="text-sm font-semibold text-white">Investment Thesis Rationale — ${symbol}</h3>
        <p class="text-xs mt-1">Autonomous research thesis record is currently synthesizing background observations.</p>
      </div>`;
    return;
  }

  const bulls = (data.bull_case || []).map(b => `<li class="flex items-start gap-2 text-xs text-green font-mono"><span>•</span><span>${b}</span></li>`).join("");
  const bears = (data.bear_case || []).map(b => `<li class="flex items-start gap-2 text-xs text-red font-mono"><span>•</span><span>${b}</span></li>`).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg space-y-4">
      <div class="flex items-center justify-between border-b border-surface-border/40 pb-3">
        <div>
          <h3 class="text-base font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">article</span>
            Research Thesis Rationale — ${(data.symbol || symbol).replace(".NS", "")}
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Autonomous Conviction Drivers & Key Catalysts</p>
        </div>
        <span class="badge badge-gold font-mono">${data.conviction_tier || "HIGH CONVICTION"}</span>
      </div>

      <div class="p-3.5 bg-surface-low rounded-lg border border-surface-border/30">
        <h4 class="text-xs font-bold text-gold uppercase font-mono mb-1">Executive Summary</h4>
        <p class="text-xs text-white leading-relaxed font-mono">${data.summary || data.thesis_statement || "Strong fundamental quality with structural margin expansion tailwinds."}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-3.5 bg-surface-low rounded-lg border border-green/20">
          <h4 class="text-xs font-bold text-green uppercase font-mono mb-2">Bull Thesis Catalysts</h4>
          <ul class="space-y-1.5">${bulls || '<li class="text-xs text-muted">High ROIC expansion & pricing power.</li>'}</ul>
        </div>
        <div class="p-3.5 bg-surface-low rounded-lg border border-red/20">
          <h4 class="text-xs font-bold text-red uppercase font-mono mb-2">Key Risk Factors</h4>
          <ul class="space-y-1.5">${bears || '<li class="text-xs text-muted">Raw material inflation & regulatory changes.</li>'}</ul>
        </div>
      </div>
    </div>`;
}
