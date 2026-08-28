// institutional_intelligence_panel.js — Institutional Intelligence UI Component
import * as api from './api.js';

export async function renderInstitutionalPanel(containerId = 'institutional-panel-container', symbol = 'SHILCHAR') {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `<div class="p-4 text-xs font-mono text-gold animate-pulse">Loading Institutional Intelligence for ${symbol}...</div>`;

  const [rankData, scoreData, altData, catalysts, concall, promoter, shareholding] = await Promise.all([
    api.loadInstitutionalRank(),
    api.loadInstitutionalScore(symbol),
    api.loadMultibaggerAltData(symbol),
    api.loadMultibaggerCatalysts(symbol),
    api.loadMultibaggerConcall(symbol),
    api.loadPromoterIntelligence(symbol),
    api.loadShareholdingPattern(symbol),
  ]);

  const score = scoreData?.institutional_conviction_score ?? 'N/A';
  const rank = rankData?.ranked_universe?.[0]?.symbol ?? 'N/A';
  const concallSentiment = concall?.sentiment_label ?? 'NEUTRAL';
  const promoterHolding = promoter?.promoter_holding_pct ?? '—';
  const fiiHolding = shareholding?.fii_holding_pct ?? '—';

  container.innerHTML = `
    <div class="bg-slate-900 border border-gold/30 rounded-lg p-5 font-sans space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-gold flex items-center gap-2">
          🏛️ Institutional Rank & Multibagger Screener — ${symbol}
        </h3>
        <span class="text-xs px-2 py-1 bg-gold/10 text-gold rounded font-mono">Tier-1 Institutional Radar</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Institutional Conviction</div>
          <div class="text-lg font-bold text-emerald-400 mt-1">${score} / 100</div>
        </div>
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Top Rated Symbol</div>
          <div class="text-lg font-bold text-gold mt-1">${rank}</div>
        </div>
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Concall Tone</div>
          <div class="text-lg font-bold text-amber-400 mt-1">${concallSentiment}</div>
        </div>
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Promoter / FII Stake</div>
          <div class="text-lg font-bold text-blue-400 mt-1">${promoterHolding}% / ${fiiHolding}%</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="bg-slate-800/40 p-3 rounded border border-slate-700/60">
          <h4 class="font-semibold text-slate-200 mb-2">📡 Alt-Data & Scuttlebutt Signals</h4>
          <p class="text-slate-400 leading-relaxed">${altData?.scuttlebutt_summary || 'No alt-data signals recorded for symbol.'}</p>
        </div>
        <div class="bg-slate-800/40 p-3 rounded border border-slate-700/60">
          <h4 class="font-semibold text-slate-200 mb-2">🚀 Growth Catalysts & Order Book</h4>
          <p class="text-slate-400 leading-relaxed">${catalysts?.catalysts_summary || 'Order book & expansion pipeline active.'}</p>
        </div>
      </div>
    </div>
  `;
}
