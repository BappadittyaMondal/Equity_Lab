/**
 * video_intelligence.js — Multilingual YouTube Video Intelligence UI Component.
 * 
 * Provides interactive transcript extraction, epistemic source tiering 
 * (TIER_1_OFFICIAL_CONCALL vs TIER_2_INFLUENCER_COMMENTARY), 
 * audited balance-sheet fact-checking, timestamped multilingual Q&A synthesis, 
 * and autonomous Platform Innovation Radar alerts.
 */

import { analyzeYouTubeVideo } from "./api.js";

export function renderVideoIntelligencePanel(containerId = "video-intelligence-panel") {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="p-4 bg-surface border border-surface-border rounded-xl space-y-4">
      <div class="flex items-center justify-between border-b border-surface-border pb-3">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-gold">smart_display</span>
          <h3 class="text-base font-bold text-white tracking-wide">Video Intelligence Analyst</h3>
        </div>
        <span class="text-[11px] font-mono text-muted bg-surface-high px-2 py-0.5 rounded border border-surface-border">
          Multilingual PIT Fact-Checker
        </span>
      </div>

      <!-- Input Form -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-3">
        <div class="md:col-span-6">
          <label class="block text-xs font-mono text-muted mb-1">YouTube URL / Video ID:</label>
          <input id="yt-url-input" type="text" placeholder="https://www.youtube.com/watch?v=... or Video ID" 
                 class="w-full bg-surface-high border border-surface-border text-xs text-white rounded px-3 py-1.5 font-mono focus:outline-none focus:ring-1 focus:ring-gold" />
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-mono text-muted mb-1">Symbol:</label>
          <input id="yt-symbol-input" type="text" placeholder="e.g. RELIANCE" 
                 class="w-full bg-surface-high border border-surface-border text-xs text-white rounded px-3 py-1.5 font-mono uppercase focus:outline-none focus:ring-1 focus:ring-gold" />
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-mono text-muted mb-1">Language:</label>
          <select id="yt-lang-select" class="w-full bg-surface-high border border-surface-border text-xs text-gold rounded px-2 py-1.5 font-mono focus:outline-none focus:ring-1 focus:ring-gold">
            <option value="en">English</option>
            <option value="hi">Hindi (हिंदी)</option>
            <option value="bn">Bengali (বাংলা)</option>
            <option value="hi-Latn">Hinglish</option>
          </select>
        </div>
        <div class="md:col-span-2 flex items-end">
          <button id="yt-analyze-btn" class="w-full bg-gold hover:bg-yellow-500 text-surface-dark font-bold font-mono text-xs py-1.5 rounded transition flex items-center justify-center gap-1">
            <span class="material-symbols-outlined text-sm">psychology</span>
            <span>Analyze</span>
          </button>
        </div>
      </div>

      <div>
        <label class="block text-xs font-mono text-muted mb-1">Investor Query / Specific Question (Optional):</label>
        <input id="yt-query-input" type="text" placeholder="e.g. What did management state regarding debt reduction, capex guidance and order book?" 
               class="w-full bg-surface-high border border-surface-border text-xs text-white rounded px-3 py-1.5 font-mono focus:outline-none focus:ring-1 focus:ring-gold" />
      </div>

      <!-- Results Container -->
      <div id="yt-results-container" class="space-y-4 pt-2 hidden"></div>
    </div>
  `;

  const analyzeBtn = document.getElementById("yt-analyze-btn");
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      const url = (document.getElementById("yt-url-input")?.value || "").trim();
      const symbol = (document.getElementById("yt-symbol-input")?.value || "").trim().toUpperCase();
      const language_pref = document.getElementById("yt-lang-select")?.value || "en";
      const query = (document.getElementById("yt-query-input")?.value || "").trim();

      if (!url) {
        alert("Please enter a valid YouTube URL or Video ID.");
        return;
      }

      const resultsDiv = document.getElementById("yt-results-container");
      if (!resultsDiv) return;

      resultsDiv.classList.remove("hidden");
      resultsDiv.innerHTML = `
        <div class="p-6 bg-surface-low rounded-lg border border-surface-border flex items-center justify-center gap-3 text-gold">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-gold border-t-transparent"></div>
          <span class="text-xs font-mono">Extracting multilingual transcript, running fact-checking & innovation radar...</span>
        </div>
      `;

      try {
        const res = await analyzeYouTubeVideo({ url, symbol, language_pref, query });
        if (!res || res.status !== "SUCCESS") {
          resultsDiv.innerHTML = `
            <div class="p-4 bg-red-950/70 border border-red-600/50 rounded-lg text-red-200 text-xs font-mono">
              <div class="font-bold mb-1 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-sm">error</span>
                <span>Analysis Failed</span>
              </div>
              <p>${res?.error || "Could not retrieve transcript or analyze video content. Ensure subtitles are accessible."}</p>
            </div>
          `;
          return;
        }

        const src = res.source_classification || {};
        const isOfficial = src.tier === "TIER_1_OFFICIAL_CONCALL";
        const tierBadgeClass = isOfficial 
          ? "bg-emerald-950/80 text-emerald-300 border-emerald-500/50" 
          : "bg-amber-950/80 text-amber-300 border-amber-500/50";

        const qa = res.qa_synthesis || {};
        const fact = res.fact_checking || {};
        const radar = res.platform_innovation_radar || {};

        resultsDiv.innerHTML = `
          <!-- Source Credibility Tier -->
          <div class="p-3 rounded-lg border ${tierBadgeClass}">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-base">${isOfficial ? "verified" : "warning"}</span>
                <span class="font-bold text-xs">${isOfficial ? "TIER 1: OFFICIAL CORPORATE DISCLOSURE" : "TIER 2: THIRD-PARTY INFLUENCER COMMENTARY"}</span>
              </div>
              <span class="font-mono text-[11px] font-bold">Credibility: ${Math.round(src.credibility_score || 70)}%</span>
            </div>
            <p class="text-[11px] opacity-90">${src.epistemic_warning || "Official earnings conference call or corporate disclosure."}</p>
          </div>

          <!-- Timestamped Q&A Synthesizer -->
          <div class="p-4 bg-surface-low rounded-lg border border-surface-border space-y-2">
            <div class="flex items-center gap-1.5 text-gold text-xs font-bold uppercase tracking-wider">
              <span class="material-symbols-outlined text-sm">question_answer</span>
              <span>Timestamped Oral Intelligence Synthesis</span>
            </div>
            <p class="text-xs text-gray-200 leading-relaxed font-sans">${qa.answer || "No specific query synthesis generated."}</p>
            ${qa.citations && qa.citations.length > 0 ? `
              <div class="pt-2 border-t border-surface-border space-y-1.5">
                <div class="text-[10px] font-mono text-muted uppercase">Verified Transcript Citations:</div>
                ${qa.citations.map(c => `
                  <div class="flex items-start gap-2 text-xs bg-surface-high p-2 rounded border border-surface-border">
                    <span class="font-mono text-gold font-bold text-[11px] shrink-0">${c.timestamp || "[00:00]"}</span>
                    <span class="text-gray-300 italic">"${c.text}"</span>
                  </div>
                `).join('')}
              </div>
            ` : ""}
          </div>

          <!-- Audited PIT Fact-Checker -->
          <div class="p-4 bg-surface-low rounded-lg border border-surface-border space-y-2">
            <div class="flex items-center gap-1.5 text-gold text-xs font-bold uppercase tracking-wider">
              <span class="material-symbols-outlined text-sm">fact_check</span>
              <span>Point-in-Time Audited Financial Fact-Check</span>
            </div>
            ${fact.discrepancies && fact.discrepancies.length > 0 ? `
              <div class="space-y-1.5">
                ${fact.discrepancies.map(d => `
                  <div class="p-2 rounded bg-amber-950/60 border border-amber-600/40 text-amber-200 text-xs">
                    ⚠️ <strong>Contradiction Detected:</strong> ${d}
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="text-xs text-emerald-400 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-sm">check_circle</span>
                <span>Oral disclosures align with audited point-in-time fundamentals (0 balance-sheet contradictions).</span>
              </div>
            `}
          </div>

          <!-- Platform Innovation Radar -->
          ${radar.has_platform_improvement_idea ? `
            <div class="p-4 bg-gold/10 border border-gold/40 rounded-lg space-y-2">
              <div class="flex items-center justify-between text-gold text-xs font-bold uppercase tracking-wider">
                <div class="flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">radar</span>
                  <span>Autonomous Platform Innovation Radar Alert</span>
                </div>
                <span class="text-[10px] font-mono bg-gold/20 px-2 py-0.5 rounded text-gold">Category: ${radar.category || "QUANTITATIVE"}</span>
              </div>
              <p class="text-xs text-gray-200"><strong>Concept Spotted:</strong> ${radar.improvement_idea || "Novel quantitative concept identified in video."}</p>
              <p class="text-xs text-muted"><strong>Target Subsystems:</strong> ${(radar.suggested_engine_targets || []).join(", ") || "Analytical Engines"}</p>
              <div class="text-[11px] text-gray-400 italic">Action Proposal: ${radar.actionable_recommendation || "Review concept for potential integration."}</div>
            </div>
          ` : `
            <div class="p-3 bg-surface-low rounded-lg border border-surface-border text-xs text-muted flex items-center justify-between">
              <span>Platform Innovation Radar: 0 novel mathematical models detected. Retail folklore filtered out.</span>
              <span class="text-emerald-400 font-mono text-[10px]">FOLKLORE FILTER ACTIVE</span>
            </div>
          `}
        `;
      } catch (err) {
        resultsDiv.innerHTML = `
          <div class="p-4 bg-red-950/70 border border-red-600/50 rounded-lg text-red-200 text-xs font-mono">
            Network error: ${err.message || "Failed to reach backend service."}
          </div>
        `;
      }
    });
  }
}

if (typeof window !== "undefined") {
  window.renderVideoIntelligencePanel = renderVideoIntelligencePanel;
}
