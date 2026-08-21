// timeline_panel.js – Corporate Milestone Timeline component
import { loadCompanyTimeline } from "./api.js";

export async function renderTimelinePanel(symbol = "RELIANCE") {
  const container = document.getElementById("timeline-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-20 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadCompanyTimeline(symbol);
  const events = (data && data.events) ? data.events : (Array.isArray(data) ? data : []);

  if (!events || events.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">timeline</span>
        <h3 class="text-sm font-semibold text-white">Corporate Timeline — ${symbol}</h3>
        <p class="text-xs mt-1">No historical business milestones or restructuring events logged for this ticker.</p>
      </div>`;
    return;
  }

  const items = events.map(ev => `
    <div class="relative pl-6 pb-4 border-l border-surface-border/60 last:border-l-0">
      <div class="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-gold"></div>
      <div class="text-xs font-mono font-bold text-gold">${ev.date || ev.year || "Historical"}</div>
      <div class="text-sm font-semibold text-white mt-0.5">${ev.title || ev.event_type || "Corporate Event"}</div>
      <p class="text-xs text-muted mt-1">${ev.description || ev.notes || ""}</p>
    </div>`).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="mb-4">
        <h3 class="text-base font-bold text-white font-mono flex items-center gap-2">
          <span class="material-symbols-outlined text-gold">timeline</span>
          Corporate Timeline & Milestone History — ${(data.symbol || symbol).replace(".NS", "")}
        </h3>
        <p class="text-xs text-muted mt-0.5 font-mono">Sequential record of earnings, acquisitions, and strategic shifts</p>
      </div>
      <div class="mt-4">
        ${items}
      </div>
    </div>`;
}
