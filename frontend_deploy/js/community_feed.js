// community_feed.js — Real-Time Community & Expert Discussion Feed Component

export function initCommunityFeed() {
  const container = document.getElementById("community-feed-body");
  if (!container) return;

  container.innerHTML = `
    <div class="p-3 bg-surface-lowest rounded border border-surface-border font-mono text-xs space-y-2">
      <div class="flex items-center justify-between border-b border-surface-border/60 pb-1.5">
        <span class="text-gold font-bold">💬 Curated Analyst & Institutional Insights</span>
        <span class="badge badge-warning text-[10px]">CURATED RESEARCH INSIGHTS</span>
      </div>
      <div class="space-y-2">
        <div class="p-2 bg-surface-low rounded border border-surface-border/40">
          <div class="flex items-center justify-between text-[11px] mb-1">
            <span class="text-white font-semibold">@AlphaTrader_IN</span>
            <span class="text-muted text-[10px]">Sample Insight</span>
          </div>
          <p class="text-cream-light text-[11px]">POLYCAB shows strong volume accumulation at ₹6,450 support level. Pre-breakout RS indicator flashing bullish §44 signals.</p>
        </div>
        <div class="p-2 bg-surface-low rounded border border-surface-border/40">
          <div class="flex items-center justify-between text-[11px] mb-1">
            <span class="text-white font-semibold">@ForensicQuant</span>
            <span class="text-muted text-[10px]">Sample Insight</span>
          </div>
          <p class="text-cream-light text-[11px]">Beneish M-Score for RELIANCE verified clean (-2.84). Governance promoter pledge ratio zero.</p>
        </div>
      </div>
    </div>
  `;
}
