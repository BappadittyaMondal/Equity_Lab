// drift_panel.js – System Model Drift & Performance Health indicator component
import { loadDriftStatus } from "./api.js";

export async function renderDriftStatusIndicator() {
  const container = document.getElementById("drift-status-container");
  if (!container) return;

  const data = await loadDriftStatus();
  if (!data) {
    container.innerHTML = `<span class="badge badge-neutral text-xs font-mono">Drift Status: UNKNOWN</span>`;
    return;
  }

  const level = data.drift_alert_level || "GREEN";
  const acc = data.rolling_30d_accuracy_pct != null ? `${data.rolling_30d_accuracy_pct.toFixed(1)}%` : "100.0%";
  const levelClass = level === "RED" ? "badge-danger" : (level === "YELLOW" ? "badge-warning" : "badge-success");

  container.innerHTML = `
    <div class="flex items-center gap-2 font-mono text-xs">
      <span class="text-muted">Model Drift:</span>
      <span class="badge ${levelClass}">${level}</span>
      <span class="text-muted hidden sm:inline">Rolling Acc: <strong class="text-white">${acc}</strong></span>
    </div>`;
}
