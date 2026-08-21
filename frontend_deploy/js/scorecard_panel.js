// scorecard_panel.js – Unified Scorecard research view component
import { loadScorecard } from "./api.js";

export async function renderScorecardPanel(symbol = "RELIANCE") {
  const container = document.getElementById("scorecard-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-20 bg-surface-high rounded mb-4"></div>
      <div class="h-4 bg-surface-high rounded w-1/2"></div>
    </div>`;

  const data = await loadScorecard(symbol);

  if (!data) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">warning</span>
        <h3 class="text-sm font-semibold text-white">Scorecard Unavailable for ${symbol}</h3>
        <p class="text-xs mt-1">Target equity ticker has insufficient coverage or data is temporarily unreachable.</p>
      </div>`;
    return;
  }

  const pillars = data.pillar_scores || {};
  const prob = (data.return_probability != null) ? (data.return_probability * 100).toFixed(1) : "—";
  const verdictClass = data.verdict === "Buy" ? "badge-success" : (data.verdict === "Strong Buy" ? "badge-gold" : "badge-neutral");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-surface-border/40">
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-xl font-bold text-white font-mono">${(data.symbol || symbol).replace(".NS", "")}</h3>
            <span class="badge ${verdictClass}">${(data.verdict || "HOLD").toUpperCase()}</span>
          </div>
          <p class="text-xs text-muted mt-1 font-mono">Unified Research Scorecard • Model ${data.model_version || "1.0"}</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-mono font-bold text-gold">${data.composite_score || 0} <span class="text-xs text-muted">/100</span></div>
          <div class="text-xs text-green font-mono">12M Outperformance Probability: ${prob}%</div>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">E1 Quality</div>
          <div class="text-lg font-mono font-bold text-white">${pillars.E1_Quality != null ? pillars.E1_Quality : "—"}</div>
          <div class="text-xs text-gold">Weight: 35%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">E2 Growth</div>
          <div class="text-lg font-mono font-bold text-white">${pillars.E2_Growth != null ? pillars.E2_Growth : "—"}</div>
          <div class="text-xs text-gold">Weight: 30%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">E3 Valuation</div>
          <div class="text-lg font-mono font-bold text-white">${pillars.E3_Valuation != null ? pillars.E3_Valuation : "—"}</div>
          <div class="text-xs text-gold">Weight: 20%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">E4 Momentum</div>
          <div class="text-lg font-mono font-bold text-white">${pillars.E4_Momentum != null ? pillars.E4_Momentum : "—"}</div>
          <div class="text-xs text-gold">Weight: 15%</div>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs font-mono p-3 bg-surface-low/50 rounded-lg">
        <span class="text-muted">Multibagger Candidate Screener Status:</span>
        <span class="${data.multibagger_status ? 'text-green font-bold' : 'text-muted'}">${data.multibagger_status ? 'QUALIFIED MULTIBAGGER CANDIDATE' : 'STANDARD CANDIDATE'}</span>
      </div>
    </div>`;
}
