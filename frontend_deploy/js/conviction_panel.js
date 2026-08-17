// conviction_panel.js – Renders institutional conviction call panel with radial gauge & engine breakdown
const API_BASE = window.API_BASE || "";

export async function renderConvictionPanel(symbol) {
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
    const resp = await fetch(`${API_BASE}/api/v1/decision/${encodeURIComponent(symbol)}`);
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

    // Determine Gauge & Verdict Color — matches backend ConvictionCall verdicts
    let gaugeColor = "#eab308"; // Gold/Yellow
    let verdictBg = "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    if (conviction_score >= 70 || verdict === "Strong Buy" || verdict === "Buy" || verdict === "Accumulate") {
      gaugeColor = "#22c55e"; // Green
      verdictBg = "bg-green-500/20 text-green-400 border-green-500/30";
    } else if (conviction_score <= 40 || verdict === "Avoid") {
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

    // Stale Data Banner State
    const staleBanner = stale ? `
      <div class="mb-3 px-3 py-1.5 bg-yellow-950/60 border border-yellow-600/50 text-yellow-200 text-xs rounded-md flex items-center gap-2">
        <span class="material-symbols-outlined text-base">history</span>
        <span>Market data snapshot is STALE. Showing cached decision calculated at ${timestamp || 'previous session'}.</span>
      </div>` : '';

    const panelHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border">
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
          </div>

          <!-- Radial Gauge -->
          <div class="flex items-center gap-3 bg-surface-low px-4 py-2 rounded-lg border">
            <div class="relative w-14 h-14 flex items-center justify-center">
              <svg class="w-14 h-14 transform -rotate-90">
                <circle cx="28" cy="28" r="22" stroke="#333" stroke-width="5" fill="transparent"/>
                <circle cx="28" cy="28" r="22" stroke="${gaugeColor}" stroke-width="5" fill="transparent"
                  stroke-dasharray="138" stroke-dashoffset="${138 - (138 * conviction_score) / 100}"
                  stroke-linecap="round"/>
              </svg>
              <span class="absolute font-mono font-bold text-sm text-white">${conviction_score}</span>
            </div>
            <div class="text-xs">
              <div class="text-muted">Conviction Score</div>
              <div class="font-mono font-semibold" style="color:${gaugeColor}">${conviction_score} / 100</div>
            </div>
          </div>
        </div>

        <!-- Primary Thesis -->
        <div class="p-3 bg-surface-low rounded-lg border mb-4">
          <div class="text-xs text-gold font-semibold uppercase tracking-wider mb-1">Primary Investment Thesis</div>
          <p class="text-sm text-gray-200 leading-relaxed">${primary_thesis || 'No primary thesis statement recorded.'}</p>
        </div>

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
  } catch (err) {
    // 3. Error State
    container.innerHTML = `
      <div class="p-6 bg-red-950/80 border border-red-600/60 rounded-xl text-red-200">
        <div class="flex items-center gap-2 mb-2 font-bold">
          <span class="material-symbols-outlined">warning</span>
          <span>Failed to load Conviction Decision</span>
        </div>
        <p class="text-xs text-red-300 mb-3">${err.message || 'Network or server error encountered.'}</p>
        <button class="px-3 py-1 bg-red-800 hover:bg-red-700 text-white font-mono text-xs rounded border"
                onclick="renderConvictionPanel('${symbol}')">
          Retry Analysis
        </button>
      </div>`;
  }
}
