import { apiFetch } from "./api.js";

export async function renderConvictionPanel(symbol, objective = "ALL", query = "") {
  const container = document.getElementById('conviction-panel');
  if (!container) return;

  if (!symbol) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-4xl mb-2 text-gold">insights</span>
        <h3 class="text-lg font-semibold text-gold">No Symbol Selected</h3>
        <p class="text-xs">Search for an Indian equity ticker above or click a stock in your watchlist.</p>
      </div>`;
    return;
  }

  // 1. Loading State (Skeleton UI)
  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-16 bg-surface-high rounded mb-4"></div>
      <div class="h-4 bg-surface-high rounded w-2/3"></div>
    </div>`;

  try {
    const params = new URLSearchParams();
    if (objective && objective !== "ALL") {
      params.append("objective", objective);
    }
    if (query && query.trim()) {
      params.append("query", query.trim());
    }
    const queryParam = params.toString() ? `?${params.toString()}` : "";
    const resp = await apiFetch(`/api/v1/decision/${encodeURIComponent(symbol)}${queryParam}`);
    if (!resp.ok) {
      if (resp.status === 404) {
        container.innerHTML = `
          <div class="p-6 bg-surface-lowest rounded-xl border text-center">
            <h3 class="text-lg font-bold text-yellow-500 mb-1">No Conviction Record Found for ${symbol}</h3>
            <p class="text-xs text-muted mb-3">Target equity ticker has not yet been processed by the Arbiter engine.</p>
          </div>`;
        return;
      }
      throw new Error(`HTTP ${resp.status}`);
    }

    const data = await resp.json();
    const {
      verdict,
      conviction_score,
      primary_thesis,
      contributing_engines = [],
      contradicting_engines = [],
      confidence_tier = "Model-dependent",
      timestamp
    } = data;

    // Data provenance: only display confidence if server provides it
    const dataConfidence = data.data_confidence_score;
    const stale = data.stale || false;

    // Determine Gauge & Verdict Color — matches backend ConvictionCall verdicts (§106)
    const normVerdict = (verdict || "").toUpperCase().trim();
    const isVeto = normVerdict === "ACTION_BLOCK" || normVerdict === "VETO" || normVerdict === "AVOID" || data.veto_applied || false;
    const isAbstain = normVerdict === "ABSTAIN" || data.abstain || false;

    let gaugeColor = "#eab308"; // Gold/Yellow
    let verdictBg = "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    if (isVeto) {
      gaugeColor = "#ef4444"; // Red
      verdictBg = "bg-red-600/30 text-red-300 border-red-500 font-black tracking-wider animate-pulse";
    } else if (isAbstain) {
      gaugeColor = "#94a3b8"; // Slate Gray
      verdictBg = "bg-slate-500/20 text-slate-300 border-slate-500/40 font-semibold";
    } else if (conviction_score >= 70 || normVerdict === "STRONG BUY" || normVerdict === "BUY" || normVerdict === "ACCUMULATE") {
      gaugeColor = "#22c55e"; // Green
      verdictBg = "bg-green-500/20 text-green-400 border-green-500/30";
    } else if (conviction_score <= 40 || normVerdict === "AVOID") {
      gaugeColor = "#ef4444"; // Red
      verdictBg = "bg-red-500/20 text-red-400 border-red-500/30";
    }

    // SVG Radial Gauge Calculation (Radius 36 -> Perimeter 226)
    const strokeDashoffset = 226 - (226 * Math.min(100, Math.max(0, conviction_score))) / 100;

    const contribHTML = contributing_engines.map(e => `
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-green-900/40 text-green-300 border border-green-700/50">
        ✓ ${e}
      </span>`).join(' ') || '<span class="text-xs text-muted">None</span>';

    const contradictHTML = contradicting_engines.map(e => `
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-red-900/40 text-red-300 border border-red-700/50">
        ⚠ ${e}
      </span>`).join(' ') || '<span class="text-xs text-muted">None</span>';

    // Governance Hard Veto & Abstention Banner States (§106)
    const vetoBanner = isVeto ? `
      <div class="mb-4 px-4 py-3 bg-red-950/90 border-2 border-red-500 text-red-100 text-sm font-bold rounded-lg flex items-center gap-3 shadow-lg ring-1 ring-red-500/50">
        <span class="material-symbols-outlined text-2xl text-red-400">gavel</span>
        <div>
          <div class="text-sm font-black tracking-wide text-red-300 uppercase">GOVERNANCE HARD VETO ACTIVE — INSTITUTIONAL CAPITAL REFUSED</div>
          <div class="text-xs font-normal text-red-200/90 mt-0.5">${data.veto_reason || data.primary_threat || data.primary_invalidation_threat || primary_thesis || "Forensic or governance violation triggered an unconditional institutional capital block."}</div>
        </div>
      </div>` : (isAbstain ? `
      <div class="mb-4 px-4 py-3 bg-slate-900/90 border-2 border-slate-500 text-slate-100 text-sm font-bold rounded-lg flex items-center gap-3 shadow-lg">
        <span class="material-symbols-outlined text-2xl text-slate-400">block</span>
        <div>
          <div class="text-sm font-black tracking-wide text-slate-300 uppercase">SIGNAL HONESTY: ENGINE ABSTENTION ACTIVE</div>
          <div class="text-xs font-normal text-slate-300/90 mt-0.5">${data.abstain_reason || data.primary_threat || data.primary_invalidation_threat || "Missing, unobserved, or conflicting Point-in-Time data forced an honest research abstention."}</div>
        </div>
      </div>` : '');

    // Stale Data Banner State
    const staleBanner = stale ? `
      <div class="mb-3 px-3 py-1.5 bg-yellow-950/60 border border-yellow-600/50 text-yellow-200 text-xs rounded-md flex items-center gap-2">
        <span class="material-symbols-outlined text-base">history</span>
        <span>Market data snapshot is STALE. Showing cached decision calculated at ${timestamp || 'previous session'}.</span>
      </div>` : '';

    const execCard = data.executive_decision_card;
    const execCardHTML = execCard ? `
      <!-- Executive Decision Card (§106 Institutional Synthesis) -->
      <div class="p-3.5 bg-surface-low rounded-lg border border-gold/30 mb-4 shadow-sm">
        <div class="flex items-center justify-between border-b border-surface-border/60 pb-2 mb-2.5">
          <div class="flex items-center gap-1.5 text-xs font-bold text-gold uppercase tracking-wider">
            <span class="material-symbols-outlined text-sm text-gold">verified</span>
            <span>Executive Decision Card</span>
          </div>
          <div class="text-[11px] font-mono px-2 py-0.5 rounded bg-surface-high border border-surface-border text-gray-300">
            Horizon: <span class="text-gold font-bold">${execCard.risk_adjusted_time_horizon || '3-12 Months'}</span>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div class="p-2 bg-surface-lowest/80 rounded border border-surface-border/40">
            <div class="text-[10px] text-green-400 font-bold uppercase tracking-wider mb-0.5">Primary Conviction Driver</div>
            <div class="text-gray-200 leading-snug">${execCard.primary_conviction_driver || 'Multi-engine quantitative confluence'}</div>
          </div>
          <div class="p-2 bg-surface-lowest/80 rounded border border-surface-border/40">
            <div class="text-[10px] text-red-400 font-bold uppercase tracking-wider mb-0.5">Primary Invalidation Threat</div>
            <div class="text-gray-200 leading-snug">${execCard.primary_invalidation_threat || 'None identified'}</div>
          </div>
        </div>
        <div class="mt-2 text-[11px] text-muted flex flex-wrap items-center justify-between gap-2">
          <span>Sizing Guideline: <strong class="text-gray-200">${execCard.capital_allocation_guideline || 'Model-dependent'}</strong></span>
          <span>Governance: <strong class="${isVeto ? 'text-red-400 font-bold' : 'text-green-400 font-semibold'}">${execCard.governance_health_verdict || 'VERIFIED'}</strong></span>
        </div>
      </div>` : '';

    const panelHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border">
        ${vetoBanner}
        ${staleBanner}
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-2xl font-bold text-gold tracking-tight">${symbol}</h2>
              <span class="px-3 py-1 text-xs font-bold font-mono rounded-full border ${verdictBg}">
                ${verdict}
              </span>
            </div>
            <p class="text-xs text-muted mt-1">
              ${dataConfidence != null ? `Data Confidence: <strong class="text-gold font-mono">${dataConfidence}%</strong> | ` : ""}Tier: <span class="font-semibold text-white">${confidence_tier}</span>
            </p>
            <div class="flex items-center gap-2 mt-2">
              <label for="conviction-objective-select" class="text-xs text-muted font-mono">Objective:</label>
              <select id="conviction-objective-select" class="bg-surface-high border border-surface-border text-xs text-gold rounded px-2 py-0.5 font-mono focus:outline-none focus:ring-1 focus:ring-gold">
                ${["ALL", "GENERAL", "TURNAROUND", "VALUE_BUYING", "SIP_COMPOUNDER", "SWING_POSITIONAL", "EARLY_MICROCAP"].map(o => `
                  <option value="${o}" ${objective === o ? "selected" : ""}>${o}</option>
                `).join('')}
              </select>
            </div>
          </div>

          <!-- Conviction Gauge -->
          <div class="flex items-center gap-3">
            <div class="text-right hidden sm:block">
              <div class="text-xs text-muted font-medium">Conviction Score</div>
              <div class="text-[10px] font-mono text-gray-400">0 - 100 Calibrated</div>
            </div>
            <div class="relative flex items-center justify-center">
              <svg class="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="22" stroke="currentColor" stroke-width="5" class="text-surface-high" fill="transparent"/>
                <circle cx="32" cy="32" r="22" stroke="${gaugeColor}" stroke-width="5" fill="transparent"
                  stroke-dasharray="138" stroke-dashoffset="${138 - (138 * conviction_score) / 100}"
                  stroke-linecap="round"/>
              </svg>
              <span class="absolute font-mono font-bold text-sm text-white">${conviction_score}</span>
            </div>
          </div>
        </div>

        <!-- Primary Thesis -->
        <div class="p-3 bg-surface-low rounded-lg border mb-4">
          <div class="text-xs text-gold font-semibold uppercase tracking-wider mb-1">Primary Investment Thesis</div>
          <p class="text-sm text-gray-200 leading-relaxed">${primary_thesis || 'No primary thesis statement recorded.'}</p>
        </div>

        ${execCardHTML}

        <!-- Strategy Engine Breakdown Matrix -->
        <details class="group border-t border-surface-border pt-3">
          <summary class="text-xs font-semibold text-gold cursor-pointer flex items-center justify-between">
            <span>Strategy Engine Breakdown (${contributing_engines.length} Contributing / ${contradicting_engines.length} Contradicting)</span>
            <span class="material-symbols-outlined text-sm group-open:rotate-180 transition-transform">expand_more</span>
          </summary>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 pt-2 text-xs">
            <div class="p-3 bg-surface-low rounded border">
              <div class="font-semibold text-green-400 mb-2">Contributing Strategies (${contributing_engines.length})</div>
              <div class="flex flex-wrap gap-1.5">${contribHTML}</div>
            </div>
            <div class="p-3 bg-surface-low rounded border">
              <div class="font-semibold text-red-400 mb-2">Contradicting Strategies (${contradicting_engines.length})</div>
              <div class="flex flex-wrap gap-1.5">${contradictHTML}</div>
            </div>
          </div>
        </details>
      </div>`;

    container.innerHTML = panelHTML;

    const objSelect = document.getElementById("conviction-objective-select");
    if (objSelect) {
      objSelect.addEventListener("change", (e) => {
        renderConvictionPanel(symbol, e.target.value, query);
      });
    }
  } catch (err) {
    // 3. Error State
    const escapedQuery = (query || '').replace(/'/g, "\\'");
    container.innerHTML = `
      <div class="p-6 bg-red-950/80 border border-red-600/60 rounded-xl text-red-200">
        <div class="flex items-center gap-2 mb-2 font-bold">
          <span class="material-symbols-outlined">warning</span>
          <span>Failed to load Conviction Decision</span>
        </div>
        <p class="text-xs text-red-300 mb-3">${err.message || 'Network or server error encountered.'}</p>
        <button class="px-3 py-1 bg-red-800 hover:bg-red-700 text-white font-mono text-xs rounded border"
                onclick="window.renderConvictionPanel ? window.renderConvictionPanel('${symbol}', '${objective}', '${escapedQuery}') : null">
          Retry Analysis
        </button>
      </div>`;
  }
}

if (typeof window !== "undefined") {
  window.renderConvictionPanel = renderConvictionPanel;
}
