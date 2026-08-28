// genai_redteam_panel.js — GenAI Red-Team & Geopolitical Risk Overlay UI Panel
import { apiFetch } from "./api.js";

export async function renderGenAIRedTeamPanel(symbol = "COFORGE") {
  const container = document.getElementById("genai-redteam-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border animate-pulse">
      <div class="h-6 w-1/3 bg-surface-high rounded mb-4"></div>
      <div class="h-20 bg-surface-high rounded"></div>
    </div>`;

  try {
    // 1. Fetch Concall Audit
    const concallResp = await apiFetch(`/api/v1/research/genai-redteam/concall-audit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol })
    });
    const concallData = concallResp.ok ? await concallResp.json() : null;

    // 2. Fetch Geopolitical Overlay
    const geoResp = await apiFetch(`/api/v1/research/genai-redteam/geopolitical-overlay/${encodeURIComponent(symbol)}`);
    const geoData = geoResp.ok ? await geoResp.json() : null;

    const riskFlags = (concallData?.flagged_concall_risks || []).map(r => `
      <div class="flex items-center justify-between p-2 bg-surface-low rounded text-xs font-mono">
        <span class="text-white font-semibold">${r.keyword}</span>
        <span class="badge badge-${r.severity === 'CRITICAL' ? 'danger' : 'warning'}">${r.risk_type} (${r.severity})</span>
      </div>`).join("");

    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border space-y-4">
        <div class="flex items-center justify-between border-b border-surface-border pb-3">
          <div>
            <h3 class="font-bold text-base text-gold">GenAI Qualitative Red-Team & Geopolitical Risk</h3>
            <p class="text-xs text-muted">Management concall sentiment & macro overlay for <span class="font-mono text-white">${symbol}</span></p>
          </div>
          <div class="font-mono text-right">
            <span class="badge ${concallData?.data_mode === 'INSUFFICIENT_DATA' ? 'badge-neutral' : 'badge-success'}">
              Data Mode: ${concallData?.data_mode || 'UNAVAILABLE'}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Concall Qualitative Audit -->
          <div class="p-3 bg-surface-low/50 rounded-lg border border-surface-border space-y-2">
            <h4 class="font-semibold text-xs text-gold uppercase tracking-wider">Earnings Concall Risk Analyst</h4>
            ${concallData?.sentiment_score != null ? `
              <div class="text-xs font-mono text-muted">
                Management Tone: <strong class="text-white">${concallData.sentiment_label}</strong> (${concallData.sentiment_score}/100)
              </div>` : '<div class="text-xs text-muted italic">No earnings call transcript supplied. Data mode honest.</div>'}
            ${riskFlags ? `<div class="space-y-1 mt-2">${riskFlags}</div>` : ''}
            <div class="text-xs text-muted font-mono mt-2">${concallData?.concall_summary || ''}</div>
          </div>

          <!-- Geopolitical Overlay -->
          <div class="p-3 bg-surface-low/50 rounded-lg border border-surface-border space-y-2">
            <h4 class="font-semibold text-xs text-gold uppercase tracking-wider">Geopolitical Sector Overlay</h4>
            ${geoData ? `
              <div class="text-xs font-mono text-muted space-y-1">
                <div>Sector: <strong class="text-white">${geoData.sector || 'GENERAL'}</strong></div>
                <div>Risk Category: <strong class="text-white">${geoData.geopolitical_risk_category || 'LOW'}</strong></div>
                <div>Multiplier Impact: <strong class="${(geoData.macro_multiplier || 1.0) >= 1.0 ? 'text-green' : 'text-red'}">${geoData.macro_multiplier || 1.0}x</strong></div>
              </div>
              <div class="text-xs text-muted mt-2 font-mono">${(geoData.key_drivers || []).join("; ")}</div>` 
              : '<div class="text-xs text-muted">Geopolitical data unavailable.</div>'}
          </div>
        </div>
      </div>`;
  } catch (err) {
    container.innerHTML = `
      <div class="p-4 bg-surface-lowest rounded-xl border border-surface-border text-center text-xs text-muted">
        GenAI Red-Team panel unavailable: ${err.message}
      </div>`;
    console.warn("GenAI Red-Team panel load failed:", err.message);
  }
}
