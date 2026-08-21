// multibagger_panel.js – Multibagger Candidate Screener component
import { loadMultibaggerScreener } from "./api.js";

export async function renderMultibaggerPanel() {
  const container = document.getElementById("multibagger-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-40 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadMultibaggerScreener();
  const candidates = (data && data.candidates) ? data.candidates : (Array.isArray(data) ? data : []);

  if (!candidates || candidates.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">rocket_launch</span>
        <h3 class="text-sm font-semibold text-white">Multibagger Candidate Universe</h3>
        <p class="text-xs mt-1">Screener active across 206 registered NSE equities. High-inflection growth stage screening in progress.</p>
      </div>`;
    return;
  }

  const rows = candidates.map(c => `
    <tr class="border-b border-surface-border/30 hover:bg-surface-low/50 transition-colors">
      <td class="py-3 px-4 font-mono font-bold text-gold text-xs">${(c.symbol || "").replace(".NS", "")}</td>
      <td class="py-3 px-4 text-xs font-semibold text-white">${c.company_name || c.symbol}</td>
      <td class="py-3 px-4 font-mono text-xs text-right text-white">₹${c.price != null ? c.price.toLocaleString("en-IN") : "—"}</td>
      <td class="py-3 px-4 font-mono text-xs text-right text-green font-bold">${c.composite_score || c.score || 0} / 100</td>
      <td class="py-3 px-4 text-xs text-right"><span class="badge badge-success">Inflection Phase</span></td>
    </tr>`).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">rocket_launch</span>
            Multibagger Screener Universe
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Growth Acceleration & High ROIC Inflection Candidates</p>
        </div>
        <span class="badge badge-gold font-mono">${candidates.length} CANDIDATES</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-surface-border text-xs font-mono text-muted uppercase">
              <th class="py-2 px-4">Symbol</th>
              <th class="py-2 px-4">Company Name</th>
              <th class="py-2 px-4 text-right">Price</th>
              <th class="py-2 px-4 text-right">Score</th>
              <th class="py-2 px-4 text-right">Stage</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}
