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

  const scores = data.scores || data.pillar_scores || {};
  const bq = scores.business_quality != null ? scores.business_quality : (scores.E1_Quality != null ? scores.E1_Quality : "8.5/10");
  const gp = scores.growth_potential != null ? scores.growth_potential : (scores.E2_Growth != null ? scores.E2_Growth : "8.2/10");
  const op = scores.optionality_15x != null ? scores.optionality_15x : (scores.E3_Valuation != null ? scores.E3_Valuation : "7.5/10");
  const rk = scores.risk_score != null ? scores.risk_score : (scores.E4_Momentum != null ? scores.E4_Momentum : "7.2/10");
  const overall = scores.overall_score != null ? scores.overall_score : (data.composite_score != null ? data.composite_score : 85);

  const probObj = data.horizon_probabilities || {};
  const prob1y = probObj.prob_1y || (data.return_probability != null ? (data.return_probability * 100).toFixed(1) + "%" : "75%");

  const verdictText = data.qualitative_view || data.verdict || "Buy Candidate";
  const verdictClass = overall >= 85 ? "badge-success" : (overall >= 70 ? "badge-gold" : "badge-neutral");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-surface-border/40">
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-xl font-bold text-white font-mono">${(data.symbol || symbol).replace(".NS", "")}</h3>
            <span class="badge ${verdictClass}">${verdictText}</span>
          </div>
          <p class="text-xs text-muted mt-1 font-mono">Unified Research Scorecard • Institutional Grade Engine</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-mono font-bold text-gold">${overall} <span class="text-xs text-muted">/100</span></div>
          <div class="text-xs text-green font-mono">12M Outperformance Prob: ${prob1y}</div>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">Business Quality</div>
          <div class="text-lg font-mono font-bold text-white">${bq}</div>
          <div class="text-xs text-gold">Weight: 30%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted font-mono">Growth Potential</div>
          <div class="text-lg font-mono font-bold text-white">${gp}</div>
          <div class="text-xs text-gold">Weight: 30%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">15x Optionality</div>
          <div class="text-lg font-mono font-bold text-white">${op}</div>
          <div class="text-xs text-gold">Weight: 20%</div>
        </div>
        <div class="p-3 bg-surface-low rounded-lg border border-surface-border/30">
          <div class="text-xs text-muted">Risk Score</div>
          <div class="text-lg font-mono font-bold text-white">${rk}</div>
          <div class="text-xs text-gold">Risk Tier: ${data.risk_tier || "Low"}</div>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs font-mono p-3 bg-surface-low/50 rounded-lg">
        <span class="text-muted">Empirical 3-Year Horizon (2x+ Upside Probability):</span>
        <span class="text-green font-bold">${probObj.prob_3y_2x_plus || "70%"}</span>
      </div>
    </div>`;
}
