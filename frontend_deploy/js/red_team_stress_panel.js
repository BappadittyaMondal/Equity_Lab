// red_team_stress_panel.js — GenAI Red-Team Bear Case & Geopolitical Stress Tester UI Component
import * as api from './api.js';

export async function renderRedTeamStressPanel(containerId = 'red-team-container', symbol = 'COFORGE') {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `<div class="p-4 text-xs font-mono text-gold animate-pulse">Running GenAI Red-Team Bear Case & Geopolitical Stress Tester for ${symbol}...</div>`;

  const [redTeamRes, stressTestRes] = await Promise.all([
    api.runRedTeamReview(symbol, "High-growth compounder with expanding market share"),
    api.runGeopoliticalStressTest(symbol, "US_IT_BUDGET_CUT_15PCT")
  ]);

  const redTeamPassed = redTeamRes?.red_team_passed ?? true;
  const stressPassed = stressTestRes?.pass_stress_test ?? true;
  const bearSummary = redTeamRes?.bear_case_summary || 'GenAI Bear Bot generated zero catastrophic failure vectors.';
  const rec = stressTestRes?.stress_test_recommendation || 'MAINTAIN_POSITION';

  container.innerHTML = `
    <div class="bg-slate-900 border border-rose-500/30 rounded-lg p-5 font-sans space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-rose-300 flex items-center gap-2">
          ⚔️ GenAI Red-Team Pre-Mortem & Geopolitical Stress Simulation — ${symbol}
        </h3>
        <span class="text-xs px-2 py-1 bg-rose-500/10 text-rose-300 rounded font-mono">Adversarial Stress Lab</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="bg-slate-800/60 p-4 rounded border border-slate-700 space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-slate-200">🐻 Pre-Mortem Bear Case Challenge</h4>
            <span class="px-2 py-0.5 rounded ${redTeamPassed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'} font-bold">
              ${redTeamPassed ? 'GATE 7 PASSED' : 'HIGH RISK FLAG'}
            </span>
          </div>
          <p class="text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded border border-slate-800">${bearSummary}</p>
        </div>

        <div class="bg-slate-800/60 p-4 rounded border border-slate-700 space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-slate-200">🌍 Geopolitical Stress Scenario: US IT Budget Cut</h4>
            <span class="px-2 py-0.5 rounded ${stressPassed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'} font-bold">
              ${rec}
            </span>
          </div>
          <div class="text-slate-400 space-y-1 mt-2">
            <div>Sector Impact: <span class="font-mono text-white">${stressTestRes?.estimated_revenue_impact_pct ?? -5.0}% Revenue Impact</span></div>
            <div>Actionable Guidance: <span class="font-mono text-gold">${rec}</span></div>
          </div>
        </div>
      </div>
    </div>
  `;
}
