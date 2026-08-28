// ai_committee_panel.js — AI Virtual Investment Committee UI Component
import * as api from './api.js';

export async function renderAICommitteePanel(containerId = 'ai-committee-container', symbol = 'SHILCHAR') {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `<div class="p-4 text-xs font-mono text-gold animate-pulse">Running Virtual AI Investment Committee Audit for ${symbol}...</div>`;

  const [govAudit, postMortem, supplyChain] = await Promise.all([
    api.loadGovernanceAudit(symbol),
    api.loadPostMortem(symbol),
    api.loadSupplyChainGraph(symbol),
  ]);

  const auditPassed = govAudit?.governance_clean ?? true;
  const postMortemStatus = postMortem?.learning_loop_status ?? 'ACTIVE';
  const suppliers = supplyChain?.tier_1_suppliers || ['N/A'];

  container.innerHTML = `
    <div class="bg-slate-900 border border-purple-500/30 rounded-lg p-5 font-sans space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-purple-300 flex items-center gap-2">
          🤖 Virtual AI Investment Committee & Governance Engine
        </h3>
        <span class="text-xs px-2 py-1 bg-purple-500/10 text-purple-300 rounded font-mono">Multi-Agent Auditor</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Governance & Related-Party Audit</div>
          <div class="text-lg font-bold ${auditPassed ? 'text-emerald-400' : 'text-rose-400'} mt-1">
            ${auditPassed ? 'PASSED (0 RPT Red Flags)' : 'WARNING (RPT Discrepancy)'}
          </div>
        </div>
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Post-Mortem Learning Loop</div>
          <div class="text-lg font-bold text-purple-300 mt-1">${postMortemStatus}</div>
        </div>
        <div class="bg-slate-800/60 p-3 rounded border border-slate-700">
          <div class="text-slate-400">Supply Chain Nodes</div>
          <div class="text-lg font-bold text-blue-400 mt-1">${suppliers.length} Tier-1 Interconnections</div>
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs font-semibold text-slate-300">Natural Language Quant Compiler</label>
        <div class="flex gap-2">
          <input id="nl-query-input" type="text" placeholder="e.g. Find high ROIC growth stocks with zero promoter pledge" 
            class="flex-1 bg-slate-950 border border-slate-700 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500" />
          <button id="nl-query-btn" class="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 text-xs font-bold rounded">
            Run Query
          </button>
        </div>
        <div id="nl-query-results" class="hidden bg-slate-950 p-3 rounded border border-purple-900 text-xs font-mono text-purple-200"></div>
      </div>
    </div>
  `;

  document.getElementById('nl-query-btn')?.addEventListener('click', async () => {
    const input = document.getElementById('nl-query-input')?.value;
    const resBox = document.getElementById('nl-query-results');
    if (!input || !resBox) return;

    resBox.classList.remove('hidden');
    resBox.textContent = 'Compiling query into SQL execution tree...';
    const res = await api.executeNLQuery(input);
    resBox.textContent = JSON.stringify(res, null, 2);
  });
}
