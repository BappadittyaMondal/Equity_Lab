// swing_alerts_panel.js – Swing Trade Alert feed component
import { loadSwingAlerts } from "./api.js";

export async function renderSwingAlertsPanel() {
  const container = document.getElementById("swing-alerts-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-24 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadSwingAlerts();
  const alerts = (data && data.alerts) ? data.alerts : (Array.isArray(data) ? data : []);

  if (!alerts || alerts.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">notifications_off</span>
        <h3 class="text-sm font-semibold text-white">No Active Swing Trade Setups</h3>
        <p class="text-xs mt-1">VPA Accumulation (B4), RS Leader (B6), Pocket Pivots (B7), and Weinstein Stage 2 (D17) scanner currently monitoring market universe.</p>
      </div>`;
    return;
  }

  const itemsHTML = alerts.map(alert => {
    const sym = (alert.symbol || "").replace(".NS", "");
    const score = alert.conviction_score || alert.score || 0;
    const setupType = alert.setup_type || alert.pattern || "Swing Setup";
    const price = alert.current_price != null ? `₹${alert.current_price.toLocaleString("en-IN")}` : "—";
    const statusClass = score >= 75 ? "badge-success" : "badge-neutral";

    return `
      <div class="p-3.5 bg-surface-low rounded-lg border border-surface-border/40 hover:border-gold/30 transition-all flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gold/10 flex items-center justify-center text-gold font-mono font-bold text-xs">
            ${sym.substring(0, 3)}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-sm font-bold text-white">${sym}</span>
              <span class="badge ${statusClass}">${setupType}</span>
            </div>
            <p class="text-xs text-muted mt-0.5 font-mono">Spot Price: ${price} • Engine Confirmation: B4/B6/B7/D17</p>
          </div>
        </div>
        <div class="text-right">
          <div class="text-base font-mono font-bold text-gold">${score} <span class="text-xs text-muted">score</span></div>
          <span class="text-xs text-green font-mono">ACTIVE SIGNAL</span>
        </div>
      </div>`;
  }).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-base font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">bolt</span>
            Swing Trade Alert Feed
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Live VPA Accumulation, RS Leaders & Stage 2 Breakouts</p>
        </div>
        <span class="badge badge-success font-mono">${alerts.length} SETUPS DETECTED</span>
      </div>

      <div class="space-y-3">
        ${itemsHTML}
      </div>
    </div>`;
}
