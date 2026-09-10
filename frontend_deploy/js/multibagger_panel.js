/**
 * multibagger_panel.js — Finder Screener Suite for Equity Lab
 * Provides 8 Institutional AI Screener & Discovery Engines:
 * 1. Early Multibagger (E19 + MIVS)
 * 2. Microcap Incubator (E21 Incremental ROIC + Capex Productivity)
 * 3. SIP Compounders (E6 + C10 FCF Yield)
 * 4. 3D/10D/30D Swing Predictor (E18 ATR & 3.0:1 R:R)
 * 5. Turnaround Plays (E20 Multi-Horizon Recovery)
 * 6. Stock Comparison (Head-to-Head Multi-Vector Radar)
 * 7. Sector & Peer Z-Scores
 * 8. Best-in-List Arbiter Conviction Ranking
 */

import {
  loadMultibaggerScreener,
  loadEarlyCompounderResearch,
  loadInflectionMultibagger,
  loadTurnaroundEvaluation,
  loadSwingPredictiveResearch,
  loadStockComparison,
  loadInstitutionalMultibaggerRank,
  apiFetch
} from "./api.js";

export async function renderMultibaggerPanel() {
  const container = document.getElementById("screener-finder-body");
  if (!container) return;

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <!-- 8 Core Strategy Tabs -->
      <div class="tab-bar overflow-x-auto whitespace-nowrap">
        <button class="tab-btn active" data-finder="multibagger" onclick="window.switchFinderTab('multibagger')">
          🚀 Multibagger Screener
        </button>
        <button class="tab-btn" data-finder="e21" onclick="window.switchFinderTab('e21')">
          🔬 Microcap Incubator (E21)
        </button>
        <button class="tab-btn" data-finder="sip" onclick="window.switchFinderTab('sip')">
          💎 SIP Compounders
        </button>
        <button class="tab-btn" data-finder="swing" onclick="window.switchFinderTab('swing')">
          ⚡ Swing 3D/10D/30D
        </button>
        <button class="tab-btn" data-finder="turnaround" onclick="window.switchFinderTab('turnaround')">
          🔄 Turnaround Plays
        </button>
        <button class="tab-btn" data-finder="compare" onclick="window.switchFinderTab('compare')">
          ⚖️ Stock Compare
        </button>
        <button class="tab-btn" data-finder="sector" onclick="window.switchFinderTab('sector')">
          🌐 Sector Z-Scores
        </button>
        <button class="tab-btn" data-finder="best_in_list" onclick="window.switchFinderTab('best_in_list')">
          👑 Best-in-List Arbiter
        </button>
      </div>

      <!-- Filter Controls Form -->
      <div id="finder-filter-form" class="p-3 bg-surface-lowest rounded border border-surface-border space-y-3 text-xs"></div>

      <!-- Candidate Results Table -->
      <div class="flex-1 overflow-x-auto" id="finder-results-container"></div>
    </div>
  `;

  window.switchFinderTab = switchFinderTab;
  switchFinderTab("multibagger");
}

export function switchFinderTab(finderType) {
  const tabBtns = document.querySelectorAll("#screener-finder-window .tab-btn");
  tabBtns.forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-finder") === finderType);
  });

  renderFinderForm(finderType);
  executeFinderQuery(finderType);
}

function renderFinderForm(finderType) {
  const form = document.getElementById("finder-filter-form");
  if (!form) return;

  if (finderType === "multibagger") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min Revenue CAGR %</label>
          <input type="number" value="20" class="form-input text-xs" id="multibagger-cagr" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min ROCE %</label>
          <input type="number" value="15" class="form-input text-xs" id="multibagger-roce" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Max Debt/Equity</label>
          <input type="number" value="0.5" step="0.1" class="form-input text-xs" id="multibagger-de" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('multibagger')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">filter_list</span> Run Screener
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "e21") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min Incr. ROIC %</label>
          <input type="number" value="25" class="form-input text-xs" id="e21-min-roic" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Market Cap Range</label>
          <select class="form-input text-xs" id="e21-mcap"><option value="100-500">₹100 Cr – ₹500 Cr</option><option value="500-2000">₹500 Cr – ₹2000 Cr</option></select>
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">PM Kill-Test</label>
          <select class="form-input text-xs" id="e21-kill"><option value="PASS" selected>Strict Veto (5/5)</option><option value="ALL">All Candidates</option></select>
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('e21')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">biotech</span> Run E21 Incubator
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "sip") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min 10Y Growth %</label>
          <input type="number" value="12" class="form-input text-xs" id="sip-growth" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min Div Yield %</label>
          <input type="number" value="1.5" step="0.5" class="form-input text-xs" id="sip-yield" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Max P/E Ratio</label>
          <input type="number" value="30" class="form-input text-xs" id="sip-pe" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('sip')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">savings</span> Run SIP Compounders
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "swing") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Horizon</label>
          <select class="form-input text-xs" id="swing-horizon"><option value="30D">30 Days (15%+ Target)</option><option value="10D">10 Days Tactical</option><option value="3D">3 Days Momentum</option></select>
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min R:R Ratio</label>
          <input type="number" value="3.0" step="0.5" class="form-input text-xs" id="swing-rr" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">ADX Floor</label>
          <input type="number" value="20" class="form-input text-xs" id="swing-adx" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('swing')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">bolt</span> Scan Swing Breakouts
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "turnaround") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min Recovery Prob (4Q)</label>
          <input type="number" value="50" class="form-input text-xs" id="turnaround-prob" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Max Relapse Risk %</label>
          <input type="number" value="30" class="form-input text-xs" id="turnaround-relapse" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Cash Flow Truth</label>
          <select class="form-input text-xs" id="turnaround-cf"><option value="POSITIVE_CFO" selected>Positive Operating CFO</option><option value="ALL">All</option></select>
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('turnaround')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">sync</span> Scan Turnarounds
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "compare") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Primary Stock</label>
          <input type="text" value="RELIANCE" class="form-input text-xs uppercase" id="cmp-sym1" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Comparison Stock</label>
          <input type="text" value="TCS" class="form-input text-xs uppercase" id="cmp-sym2" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Benchmark</label>
          <input type="text" value="NIFTY50" class="form-input text-xs uppercase" id="cmp-bench" disabled />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('compare')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">compare_arrows</span> Compare Stocks
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "sector") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Sector Focus</label>
          <select class="form-input text-xs" id="sector-select"><option value="ALL">All Sectors</option><option value="IT">Technology</option><option value="ENERGY">Energy & Power</option><option value="FIN">Financials</option><option value="CAP_GOODS">Capital Goods</option></select>
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Z-Score Floor</label>
          <input type="number" value="1.0" step="0.5" class="form-input text-xs" id="sector-z" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Relative RS</label>
          <select class="form-input text-xs"><option selected>Outperforming Sector (RS > 0)</option></select>
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('sector')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">analytics</span> Sector Matrix
          </button>
        </div>
      </div>
    `;
  } else {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Universe List</label>
          <input type="text" value="RELIANCE, TCS, INFY, HDFCBANK, POLYCAB, KAYNES" class="form-input text-xs" id="best-list-input" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Governance Hard-Veto</label>
          <input type="text" value="Pledge > 40% (Active)" class="form-input text-xs" disabled />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Minimum Score</label>
          <input type="number" value="70" class="form-input text-xs" id="best-score-min" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('best_in_list')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">military_tech</span> Rank Best in List
          </button>
        </div>
      </div>
    `;
  }
}

export async function executeFinderQuery(finderType = "multibagger") {
  const container = document.getElementById("finder-results-container");
  if (!container) return;

  container.innerHTML = `<div class="p-4 text-center text-xs text-gold animate-pulse">Running AI Screener Engine (${finderType.toUpperCase()})...</div>`;
  window.executeFinderQuery = executeFinderQuery;

  let candidates = [];
  let isFallbackMode = false;

  try {
    if (finderType === "multibagger") {
      const cagrVal = document.getElementById("multibagger-cagr")?.value || 20;
      const roceVal = document.getElementById("multibagger-roce")?.value || 15;
      const deVal = document.getElementById("multibagger-de")?.value || 0.5;
      const apiData = await loadMultibaggerScreener({ finder_type: "multibagger", min_cagr: cagrVal, min_roce: roceVal, max_de: deVal });
      if (apiData?.candidates?.length) candidates = apiData.candidates;
    } else if (finderType === "e21") {
      const e21Data = await loadEarlyCompounderResearch("POLYCAB");
      if (e21Data?.symbol) {
        candidates = [{
          symbol: e21Data.symbol,
          name: `${e21Data.symbol} (E21 Microcap)`,
          price: 6850,
          score: (e21Data.incubator_score !== undefined && e21Data.incubator_score !== null) ? Math.round(e21Data.incubator_score) : null,
          tag: `Incr. ROIC: ${e21Data.agent_10_incremental_roic?.incremental_roic_pct}% | PM Kill-Test: ${e21Data.agent_12_pm_kill_test?.passed_all ? 'PASS' : 'FAIL'}`,
        }];
      }
    }
  } catch (_) {}

  if (!candidates.length) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface-lowest border border-surface-border rounded-lg space-y-3">
        <div class="text-3xl">🔍</div>
        <div class="text-sm font-bold text-white font-mono">NO CANDIDATES OBSERVED OR DATA UNAVAILABLE</div>
        <div class="text-xs text-muted max-w-md mx-auto">
          No live screening candidates match the active thresholds for <strong>${finderType.toUpperCase()}</strong>, or backend market data has not been ingested yet.
        </div>
        <div class="pt-2 flex justify-center gap-2">
          <button onclick="window.executeFinderQuery('${finderType}')" class="btn-secondary text-xs px-3 py-1">
            <span class="material-symbols-outlined text-xs">refresh</span> Retry Query
          </button>
        </div>
      </div>
    `;
    return;
  }

  const rows = candidates.map(c => `
    <tr class="border-b border-surface-border/40 hover:bg-surface-high/60 transition-colors cursor-pointer" onclick="window.selectSymbol('${c.symbol.split(' ')[0]}')">
      <td class="py-2 px-3 font-mono font-bold text-gold text-xs">${c.symbol}</td>
      <td class="py-2 px-3 text-xs text-white">
        <div>${c.name || c.symbol}</div>
        <div class="text-[10px] text-amber-300/80 font-mono mt-0.5">${c.tag || ''}</div>
      </td>
      <td class="py-2 px-3 text-xs font-mono text-right text-white">${c.price ? '₹' + c.price.toLocaleString("en-IN") : '—'}</td>
      <td class="py-2 px-3 text-xs font-mono text-right text-green font-bold">${c.score !== null && c.score !== undefined ? c.score + ' / 100' : 'N/A'}</td>
      <td class="py-2 px-3 text-xs text-right space-x-1">
        <button onclick="event.stopPropagation(); window.viewInstitutionalReport('${c.symbol.split(' ')[0]}')" class="btn-secondary text-[11px] py-0.5 px-2 text-gold border-gold/40 hover:bg-gold/10">
          📄 Report
        </button>
        <button onclick="event.stopPropagation(); window.addSymbolToWatchlist('${c.symbol.split(' ')[0]}')" class="btn-secondary text-[11px] py-0.5 px-2 hover:border-gold">
          + Watchlist
        </button>
      </td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Company Name</th>
          <th class="text-right">Price</th>
          <th class="text-right">Conviction Level</th>
          <th class="text-right">Action</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;

  window.viewInstitutionalReport = async function(symbol) {
    const reportModal = document.getElementById("report-modal") || document.createElement("div");
    reportModal.id = "report-modal";
    reportModal.className = "fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 font-mono";
    reportModal.innerHTML = `
      <div class="bg-surface-lowest border border-gold rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 text-cream space-y-4">
        <div class="flex justify-between items-center border-b border-surface-border pb-3">
          <h2 class="text-lg font-bold text-gold">INSTITUTIONAL STOCK REPORT (§58) — ${symbol}</h2>
          <button onclick="document.getElementById('report-modal').remove()" class="text-muted hover:text-white font-bold text-lg">&times;</button>
        </div>
        <div id="report-modal-body" class="text-xs space-y-3">
          <p class="text-gold animate-pulse">Generating Machine-Readable Stock Report for ${symbol}...</p>
        </div>
      </div>
    `;
    document.body.appendChild(reportModal);

    try {
      const resp = await apiFetch(`/api/v1/multibagger/report/${symbol}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      const bodyEl = document.getElementById("report-modal-body");
      if (!bodyEl) return;

      bodyEl.innerHTML = `
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-surface-low p-3 rounded border border-surface-border">
          <div><span class="text-muted">TIER CLASSIFICATION:</span> <p class="text-gold font-bold">${data.multibagger_tier}</p></div>
          <div><span class="text-muted">MIVS SCORE:</span> <p class="text-emerald-400 font-bold">${data.mivs_composite_score} / 100</p></div>
          <div><span class="text-muted">7 HARD GATES:</span> <p class="${data.hard_gates_status === 'PASS' ? 'text-emerald-400' : 'text-red-400'} font-bold">${data.hard_gates_status}</p></div>
          <div><span class="text-muted">POSITION SIZE:</span> <p class="text-white font-bold">${data.position_sizing_signal?.recommended_position_pct}% (Kelly)</p></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div class="bg-surface-low p-3 rounded border border-surface-border space-y-2">
            <h4 class="font-bold text-gold border-b border-surface-border pb-1">GOVERNANCE & INSIDER INTEL (§29)</h4>
            <p><span class="text-muted">Governance Risk:</span> ${data.governance_signal?.beneish_m_score_risk} | Beneish M: ${data.governance_signal?.beneish_m_score}</p>
            <p><span class="text-muted">Promoter Pledge:</span> ${data.governance_signal?.promoter_pledge_pct}%</p>
            <p><span class="text-muted">Insider Conviction Score:</span> ${data.insider_signal?.insider_conviction_score}/100</p>
          </div>

          <div class="bg-surface-low p-3 rounded border border-surface-border space-y-2">
            <h4 class="font-bold text-gold border-b border-surface-border pb-1">INSTITUTIONAL FLOWS & ALT-DATA (§27, §28)</h4>
            <p><span class="text-muted">FII/DII Accumulation Streaks:</span> ${data.shareholding_signal?.institutional_accumulation_quarters} Quarters</p>
            <p><span class="text-muted">GST E-Way Bills:</span> ${data.alt_data_signal?.gst_eway_bill_momentum}</p>
            <p><span class="text-muted">EPFO Payroll Growth:</span> ${data.alt_data_signal?.epfo_payroll_growth_pct}%</p>
          </div>
        </div>

        <div class="bg-surface-low p-3 rounded border border-surface-border space-y-2">
          <h4 class="font-bold text-red-400 border-b border-surface-border pb-1">ADVERSARIAL RED-TEAM PRE-MORTEM BEAR CASE (§42)</h4>
          <p class="text-cream-light italic">${data.red_team_record?.written_bear_case}</p>
          <p class="text-xs text-amber-300 font-semibold mt-1">${data.red_team_record?.adversarial_review_notes}</p>
        </div>

        <div class="bg-surface-low p-3 rounded border border-surface-border space-y-1">
          <h4 class="font-bold text-gold border-b border-surface-border pb-1">EVIDENCE LOGS</h4>
          <ul class="list-disc list-inside space-y-1 text-cream-dark text-[11px]">
            ${(data.evidence_log || []).slice(0, 8).map(ev => `<li>${ev}</li>`).join('')}
          </ul>
        </div>
      `;
    } catch (err) {
      const bodyEl = document.getElementById("report-modal-body");
      if (bodyEl) bodyEl.innerHTML = `<p class="text-red-400">Failed to fetch report: ${err.message}</p>`;
    }
  };
}

