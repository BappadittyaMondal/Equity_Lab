/**
 * multibagger_panel.js — Finder Screener Suite for StockAnalyzer
 * Provides 4 quantitative AI screener engines: Multibagger, SIP Compounder, Swing Breakout, and Turnaround.
 */

import { loadMultibaggerScreener } from "./api.js";

export async function renderMultibaggerPanel() {
  const container = document.getElementById("screener-finder-body");
  if (!container) return;

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <!-- Screener Strategy Tabs -->
      <div class="tab-bar">
        <button class="tab-btn active" data-finder="multibagger" onclick="window.switchFinderTab('multibagger')">
          🚀 Multibagger Screener
        </button>
        <button class="tab-btn" data-finder="sip" onclick="window.switchFinderTab('sip')">
          💎 SIP Compounders
        </button>
        <button class="tab-btn" data-finder="swing" onclick="window.switchFinderTab('swing')">
          ⚡ Swing Breakouts
        </button>
        <button class="tab-btn" data-finder="turnaround" onclick="window.switchFinderTab('turnaround')">
          🔄 Turnaround Plays
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
  } else if (finderType === "sip") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min 10Y Growth %</label>
          <input type="number" value="12" class="form-input text-xs" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min Div Yield %</label>
          <input type="number" value="2.0" step="0.5" class="form-input text-xs" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Max P/E Ratio</label>
          <input type="number" value="25" class="form-input text-xs" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('sip')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">filter_list</span> Run Screener
          </button>
        </div>
      </div>
    `;
  } else if (finderType === "swing") {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Min Price Breakout %</label>
          <input type="number" value="4.5" step="0.5" class="form-input text-xs" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min Volume Spike</label>
          <input type="number" value="2.0" step="0.5" class="form-input text-xs" placeholder="2.0x 20-MA Vol" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Min RSI (14)</label>
          <input type="number" value="65" class="form-input text-xs" />
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('swing')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">filter_list</span> Run Screener
          </button>
        </div>
      </div>
    `;
  } else {
    form.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <label class="block text-muted font-mono mb-1">Net Margin Expansion YOY</label>
          <input type="number" value="3.0" step="0.5" class="form-input text-xs" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Debt Reduction YOY %</label>
          <input type="number" value="15" class="form-input text-xs" />
        </div>
        <div>
          <label class="block text-muted font-mono mb-1">Management Change</label>
          <select class="form-input text-xs"><option>Any</option><option selected>Yes</option></select>
        </div>
        <div class="flex items-end">
          <button onclick="window.executeFinderQuery('turnaround')" class="btn-primary text-xs w-full py-1.5 justify-center">
            <span class="material-symbols-outlined text-xs">filter_list</span> Run Screener
          </button>
        </div>
      </div>
    `;
  }
}

export async function executeFinderQuery(finderType = "multibagger") {
  const container = document.getElementById("finder-results-container");
  if (!container) return;

  container.innerHTML = `<div class="p-4 text-center text-xs text-gold animate-pulse">Running AI Screener Engine...</div>`;

  window.executeFinderQuery = executeFinderQuery;

  let candidates = [];
  let isFallbackMode = false;
  try {
    const apiData = await loadMultibaggerScreener();
    if (apiData && apiData.candidates && apiData.candidates.length > 0) {
      candidates = apiData.candidates;
    }
  } catch (_) {}

  // Fallback curated mock data per strategy
  if (!candidates.length) {
    isFallbackMode = true;
    if (finderType === "multibagger") {
      candidates = [
        { symbol: "POLYCAB", name: "Polycab India Ltd", price: 6850, score: 94, cagr: "28.5%", roce: "24.2%", de: "0.08" },
        { symbol: "KEI", name: "KEI Industries Ltd", price: 4220, score: 91, cagr: "24.1%", roce: "22.8%", de: "0.12" },
        { symbol: "TRENT", name: "Trent Ltd", price: 7100, score: 89, cagr: "35.2%", roce: "19.5%", de: "0.45" },
        { symbol: "DIXON", name: "Dixon Technologies", price: 12400, score: 87, cagr: "31.0%", roce: "26.4%", de: "0.32" },
      ];
    } else if (finderType === "sip") {
      candidates = [
        { symbol: "TCS", name: "Tata Consultancy Services", price: 4250, score: 96, cagr: "14.2%", yield: "2.3%", pe: "27.5" },
        { symbol: "HDFCBANK", name: "HDFC Bank Ltd", price: 1640, score: 95, cagr: "18.0%", yield: "1.2%", pe: "18.5" },
        { symbol: "INFY", name: "Infosys Ltd", price: 1860, score: 92, cagr: "12.5%", yield: "2.5%", pe: "24.1" },
        { symbol: "TITAN", name: "Titan Company Ltd", price: 3450, score: 90, cagr: "20.1%", yield: "0.8%", pe: "78.2" },
      ];
    } else if (finderType === "swing") {
      candidates = [
        { symbol: "BHEL", name: "Bharat Heavy Electricals", price: 295, score: 88, breakout: "+6.8%", volSpike: "3.4x", rsi: "74" },
        { symbol: "HAL", name: "Hindustan Aeronautics", price: 4680, score: 93, breakout: "+5.2%", volSpike: "2.8x", rsi: "71" },
        { symbol: "BEL", name: "Bharat Electronics Ltd", price: 310, score: 90, breakout: "+4.1%", volSpike: "2.2x", rsi: "68" },
      ];
    } else {
      candidates = [
        { symbol: "SUZLON", name: "Suzlon Energy Ltd", price: 78, score: 86, margin: "+8.2%", debtCut: "-45%", mgmt: "Reformed" },
        { symbol: "YESBANK", name: "Yes Bank Ltd", price: 24, score: 78, margin: "+2.1%", debtCut: "-20%", mgmt: "SBI Backed" },
      ];
    }
  }

  const rows = candidates.map(c => `
    <tr class="border-b border-surface-border/40 hover:bg-surface-high/60 transition-colors cursor-pointer" onclick="window.selectSymbol('${c.symbol}')">
      <td class="py-2 px-3 font-mono font-bold text-gold text-xs">${c.symbol}</td>
      <td class="py-2 px-3 text-xs text-white">${c.name || c.symbol}</td>
      <td class="py-2 px-3 text-xs font-mono text-right text-white">₹${c.price ? c.price.toLocaleString("en-IN") : "—"}</td>
      <td class="py-2 px-3 text-xs font-mono text-right text-green font-bold">${c.score || 85} / 100</td>
      <td class="py-2 px-3 text-xs text-right space-x-1">
        <button onclick="event.stopPropagation(); window.viewInstitutionalReport('${c.symbol}')" class="btn-secondary text-[11px] py-0.5 px-2 text-gold border-gold/40 hover:bg-gold/10">
          📄 Report (§58)
        </button>
        <button onclick="event.stopPropagation(); window.addSymbolToWatchlist('${c.symbol}')" class="btn-secondary text-[11px] py-0.5 px-2 hover:border-gold">
          + Watchlist
        </button>
      </td>
    </tr>
  `).join("");

  const fallbackBanner = isFallbackMode ? `
    <div class="p-2 mb-2.5 bg-amber-950/60 border border-amber-500/50 rounded-lg text-amber-200 text-xs flex items-center justify-between font-mono shadow-inner">
      <span class="flex items-center gap-1.5">
        <span class="text-amber-400">⚠️</span>
        <strong>DEMO DATA MODE</strong>: Displaying curated candidate presets (Backend unauthenticated or offline).
      </span>
      <span class="text-[10px] text-amber-300/70 bg-amber-900/50 px-1.5 py-0.5 rounded">Set X-API-Key for Live Engine Results</span>
    </div>
  ` : '';

  container.innerHTML = `
    ${fallbackBanner}
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
      const apiKey = localStorage.getItem("equity_lab_api_key") || "demo-key";
      const resp = await fetch(`/api/v1/multibagger/report/${symbol}`, {
        headers: { "X-API-Key": apiKey }
      });
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

