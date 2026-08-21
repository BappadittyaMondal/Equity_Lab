// cagr_matrix_panel.js – CAGR Growth Sensitivity Matrix component
import { loadCAGRMatrix } from "./api.js";

export async function renderCAGRMatrixPanel(symbol = "RELIANCE") {
  const container = document.getElementById("cagr-matrix-panel");
  if (!container) return;

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 animate-pulse">
      <div class="h-6 bg-surface-high rounded w-1/3 mb-4"></div>
      <div class="h-32 bg-surface-high rounded mb-4"></div>
    </div>`;

  const data = await loadCAGRMatrix(symbol);

  if (!data || !data.matrix || data.matrix.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted">
        <span class="material-symbols-outlined text-3xl mb-2 text-gold">grid_off</span>
        <h3 class="text-sm font-semibold text-white">CAGR Matrix Unavailable for ${symbol}</h3>
        <p class="text-xs mt-1">Requires baseline EPS & revenue estimates for sensitivity projection.</p>
      </div>`;
    return;
  }

  const rowsHTML = data.matrix.map(row => {
    const scenario = (row.scenario || row.growth_rate_pct != null ? `${row.growth_rate_pct}%` : "—");
    const p1y = row.price_1y != null ? `₹${row.price_1y.toLocaleString("en-IN")}` : "—";
    const c1y = row.cagr_1y != null ? `${row.cagr_1y.toFixed(1)}%` : "—";
    const p3y = row.price_3y != null ? `₹${row.price_3y.toLocaleString("en-IN")}` : "—";
    const c3y = row.cagr_3y != null ? `${row.cagr_3y.toFixed(1)}%` : "—";
    const p5y = row.price_5y != null ? `₹${row.price_5y.toLocaleString("en-IN")}` : "—";
    const c5y = row.cagr_5y != null ? `${row.cagr_5y.toFixed(1)}%` : "—";
    const isBaseline = row.is_baseline ? "bg-gold/10 font-bold border-l-2 border-gold" : "";

    return `
      <tr class="border-b border-surface-border/30 hover:bg-surface-low/50 transition-colors ${isBaseline}">
        <td class="py-2.5 px-3 font-mono font-semibold text-gold text-xs">${scenario}</td>
        <td class="py-2.5 px-3 font-mono text-white text-xs text-right">${p1y} <span class="text-muted">(${c1y})</span></td>
        <td class="py-2.5 px-3 font-mono text-white text-xs text-right">${p3y} <span class="text-muted">(${c3y})</span></td>
        <td class="py-2.5 px-3 font-mono text-white text-xs text-right">${p5y} <span class="text-muted">(${c5y})</span></td>
      </tr>`;
  }).join("");

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-base font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">table_chart</span>
            CAGR Sensitivity Matrix — ${(data.symbol || symbol).replace(".NS", "")}
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">1Y, 3Y, 5Y Price Target & CAGR Projections across Revenue Scenarios</p>
        </div>
        <div class="text-xs font-mono text-muted">
          Current Price: <strong class="text-white">₹${data.current_price != null ? data.current_price.toLocaleString("en-IN") : "—"}</strong>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-surface-border text-xs font-mono text-muted uppercase">
              <th class="py-2 px-3">Revenue Growth</th>
              <th class="py-2 px-3 text-right">1-Year Target (CAGR)</th>
              <th class="py-2 px-3 text-right">3-Year Target (CAGR)</th>
              <th class="py-2 px-3 text-right">5-Year Target (CAGR)</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHTML}
          </tbody>
        </table>
      </div>
    </div>`;
}
