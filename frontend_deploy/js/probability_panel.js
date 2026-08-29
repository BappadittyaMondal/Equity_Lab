// probability_panel.js – Return Probability Engine component
import { fetchReturnProbability } from "./api.js";

export async function renderProbabilityPanel() {
  const container = document.getElementById("probability-panel");
  if (!container) return;

  const res = await fetchReturnProbability(80, 12);
  const hasData = res && (res.outperformance_probability != null || res.probability_above_threshold_pct != null);
  const rawProb = res ? (res.outperformance_probability != null ? res.outperformance_probability * 100 : res.probability_above_threshold_pct) : null;
  const prob = (rawProb != null && !isNaN(rawProb)) ? rawProb.toFixed(1) : "--";
  const rawSample = (res && res.sample_size != null) ? res.sample_size : (res && res.sample_count != null ? res.sample_count : null);
  const sampleSize = (typeof rawSample === "number" && rawSample > 0) ? rawSample : null;

  const calibrationText = "Calibrated via Logistic + GBDT Ensemble";
  const sampleText = sampleSize 
    ? `Trained on ${sampleSize.toLocaleString()} validated ledger outcomes`
    : (hasData ? `Model recalibrating on verified market outcomes` : `Data unavailable — retrying calibration engine`);

  container.innerHTML = `
    <div class="p-6 bg-surface-lowest rounded-xl border border-surface-border/50 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-white font-mono flex items-center gap-2">
            <span class="material-symbols-outlined text-gold">query_stats</span>
            Return Probability Engine
          </h3>
          <p class="text-xs text-muted mt-0.5 font-mono">Calibrated Empirical Outperformance Projections</p>
        </div>
        ${!hasData ? `<span class="px-2 py-0.5 text-xs font-mono rounded bg-red/10 text-red border border-red/20">DATA_UNAVAILABLE</span>` : ''}
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 bg-surface-low rounded-lg border border-surface-border/40">
          <div class="text-xs text-muted font-mono">Composite Score 80+ Benchmark</div>
          <div class="text-3xl font-mono font-bold ${hasData ? 'text-gold' : 'text-muted'} mt-1">${prob}${hasData ? '%' : ''}</div>
          <div class="text-xs ${hasData ? 'text-green' : 'text-muted'} mt-1 font-mono">${hasData ? '12-Month Expected Outperformance Probability' : 'Model Output Pending'}</div>
        </div>
        <div class="p-4 bg-surface-low rounded-lg border border-surface-border/40">
          <div class="text-xs text-muted font-mono">Model Calibration</div>
          <div class="text-sm font-mono text-white mt-1">${calibrationText}</div>
          <div class="text-xs text-muted mt-1 font-mono">${sampleText}</div>
        </div>
      </div>
    </div>`;
}

