// ai_committee_panel.js — Virtual Investment Committee UI Panel
import { apiFetch } from "./api.js";

export async function renderAICommitteePanel(symbol = "SHILCHAR") {
  const container = document.getElementById("ai-committee-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border animate-pulse">
      <div class="h-6 w-1/3 bg-surface-high rounded mb-4"></div>
      <div class="h-24 bg-surface-high rounded mb-2"></div>
    </div>`;

  try {
    const resp = await apiFetch(`/api/v1/research/ai-committee/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    const opinions = data.agent_opinions || [];
    const opinionsHTML = opinions.map(op => {
      const voteBadgeClass = op.vote === 'APPROVE' ? 'badge-success' : (op.vote === 'REJECT' ? 'badge-danger' : 'badge-warning');
      const findingsList = (op.key_findings || []).map(f => `<li class="text-xs text-muted">• ${f}</li>`).join("");
      const concernsList = (op.risk_concerns || []).map(c => `<li class="text-xs text-red">• ${c}</li>`).join("");

      return `
        <div class="p-3 bg-surface-low rounded border border-surface-border/50">
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-sm text-white">${op.agent_name || op.role}</span>
            <span class="badge ${voteBadgeClass}">${op.vote} (${op.conviction_weight}%)</span>
          </div>
          ${findingsList ? `<ul class="space-y-1 mb-2">${findingsList}</ul>` : ''}
          ${concernsList ? `<ul class="space-y-1">${concernsList}</ul>` : ''}
        </div>`;
    }).join("");

    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border space-y-4">
        <div class="flex items-center justify-between border-b border-surface-border pb-3">
          <div>
            <h3 class="font-bold text-base text-gold">Investment Committee Boardroom Consensus</h3>
            <p class="text-xs text-muted">Deterministic 4-Vector Investment Committee Evaluation for <span class="font-mono text-white">${data.symbol || symbol}</span></p>
          </div>
          <div class="text-right font-mono">
            <div class="text-xl font-extrabold ${data.consensus_verdict === 'APPROVED' ? 'text-green' : 'text-amber-400'}">${data.consensus_verdict || 'REVIEW'}</div>
            <div class="text-xs text-muted">Conviction: ${data.ic_conviction_score || 0}/100</div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${opinionsHTML || '<p class="text-xs text-muted">No committee opinions generated.</p>'}
        </div>

        ${data.ic_memo_summary ? `
          <div class="p-3 bg-surface-high/30 rounded border border-surface-border text-xs text-muted font-mono">
            <strong class="text-gold block mb-1">Executive IC Memo:</strong>
            ${data.ic_memo_summary}
          </div>` : ''}
      </div>`;
  } catch (err) {
    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border text-center text-xs text-muted">
        Investment Committee panel unavailable: ${err.message}
      </div>`;
    console.warn("AI Committee panel load failed:", err.message);
  }
}
