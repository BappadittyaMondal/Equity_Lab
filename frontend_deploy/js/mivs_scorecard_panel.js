import { loadMIVSScore } from "./api.js";

export async function renderMIVSScorecardPanel(containerId = "mivs-scorecard-panel", symbol = "RELIANCE") {
  const el = document.getElementById(containerId);
  if (!el) return;

  el.innerHTML = `
    <div class="p-3 bg-surface-lowest rounded border border-surface-border font-mono text-xs text-muted animate-pulse">
      Loading MIVS Scorecard for ${symbol}...
    </div>
  `;

  const mivsData = await loadMIVSScore(symbol);
  renderMIVSScorecard(containerId, mivsData);
}

export function renderMIVSScorecard(containerId, mivsData) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!mivsData) {
    el.innerHTML = `
      <div class="p-3 bg-surface-lowest rounded border border-surface-border font-mono text-xs text-amber-400">
        ⚠️ MIVS Vector Scorecard unavailable for selected symbol.
      </div>
    `;
    return;
  }

  const score = mivsData.mivs_score ?? 75.0;
  const passed = mivsData.passed_hard_gates ?? true;
  const verdict = mivsData.verdict ?? (passed ? "Buy" : "Avoid");
  const reasons = mivsData.gate_reasons || [];
  const dims = mivsData.dimension_scores || {};
  const sectorPercentile = mivsData.sector_relative_percentile ?? 50.0;

  const scoreColor = !passed ? "text-red-400" : (score >= 70 ? "text-emerald-400" : (score >= 50 ? "text-amber-400" : "text-red-400"));
  const gateBadge = passed 
    ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-700">7 HARD GATES PASSED</span>`
    : `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950 text-red-300 border border-red-700">HARD GATE VETO</span>`;

  let html = `
    <div class="p-4 bg-surface-lowest rounded-lg border border-gold/40 space-y-3 font-mono">
      <div class="flex items-center justify-between border-b border-surface-border/60 pb-2">
        <div>
          <span class="text-xs text-muted uppercase tracking-wider">100-Point MIVS Score (§51, §52)</span>
          <h3 class="text-xl font-bold font-serif ${scoreColor}">${score.toFixed(1)} <span class="text-xs font-sans text-cream-dark">/ 100</span></h3>
          <span class="text-[10px] text-gold font-sans font-semibold">Sector Rank: ${sectorPercentile.toFixed(1)}th Percentile</span>
        </div>
        <div class="text-right">
          ${gateBadge}
          <p class="text-xs font-bold text-gold mt-1 uppercase">${verdict}</p>
        </div>
      </div>
  `;

  if (!passed && reasons.length > 0) {
    html += `
      <div class="p-2 bg-red-950/40 border border-red-800/60 rounded text-xs text-red-300 space-y-1">
        <span class="font-bold text-red-400">Veto Rejections (7 Hard Gates):</span>
        <ul class="list-disc list-inside space-y-0.5 text-[11px]">
          ${reasons.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  html += `
      <div class="space-y-2 pt-1 text-xs">
        <span class="text-[11px] text-muted uppercase tracking-wider font-bold">9-Component Vector Breakdown</span>
  `;

  const dimNames = {
    "FUNDAMENTAL_INFLECTION": "Fundamental Inflection (22%)",
    "BUSINESS_INDUSTRY_QUALITY": "Business & Moat Quality (18%)",
    "INCREMENTAL_ECONOMICS": "Incremental ROIC (13%)",
    "GROWTH_AND_RUNWAY": "Growth & TAM Runway (12%)",
    "EXPECTATION_GAP_REVISIONS": "Expectation Gap & Revisions (10%)",
    "GOVERNANCE_PROMOTER_BEHAVIOUR": "Governance & Insider (8%)",
    "VALUATION_ASYMMETRY": "Valuation Asymmetry (8%)",
    "MARKET_CONFIRMATION_ALT_DATA": "Alt-Data & Confirmation (5%)",
    "EVIDENCE_CONFIDENCE": "Evidence Confidence (4%)"
  };

  for (const [key, label] of Object.entries(dimNames)) {
    const dimObj = dims[key] || { raw_score: 50.0, weighted_score: 5.0, percentile_rank: 50.0 };
    const rawVal = dimObj.raw_score ?? 50.0;
    const pRank = dimObj.percentile_rank ?? 50.0;
    const barWidth = Math.min(100, Math.max(0, rawVal));

    html += `
      <div>
        <div class="flex justify-between text-[11px] mb-0.5">
          <span class="text-cream-light">${label}</span>
          <span class="text-gold font-bold">${rawVal.toFixed(1)} <span class="text-[9px] text-muted">(${pRank.toFixed(0)}th %ile)</span></span>
        </div>
        <div class="w-full h-1.5 bg-surface-low rounded overflow-hidden">
          <div class="h-full bg-gold transition-all duration-500" style="width: ${barWidth}%"></div>
        </div>
      </div>
    `;
  }

  html += `</div></div>`;
  el.innerHTML = html;
}

