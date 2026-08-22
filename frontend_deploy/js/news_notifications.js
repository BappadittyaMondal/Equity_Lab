/**
 * news_notifications.js — News Intelligence Popup & Alert Engine for StockAnalyzer
 * Displays real-time headlines with AI sentiment tagging (Positive, Neutral, Negative)
 * and notification alert popups for technical breakouts and price triggers.
 */

const DEFAULT_NEWS = [
  {
    id: 1,
    title: "RBI Repo Rate Announcement: Policy stance remains neutral with focus on inflation calibration",
    source: "RBI Press Release",
    time: "20m ago",
    sentiment: "POSITIVE",
    ticker: "BANKNIFTY",
    summary: "Reserve Bank of India retains interest rate policy while projecting robust 7.2% GDP growth for current fiscal year."
  },
  {
    id: 2,
    title: "Reliance Industries commissioning 20GW Green Energy Gigafactory ahead of schedule",
    source: "ET Markets",
    time: "45m ago",
    sentiment: "POSITIVE",
    ticker: "RELIANCE",
    summary: "Capex rollout for solar cell and hydrogen electrolyzer units achieves 90% completion."
  },
  {
    id: 3,
    title: "Polycab India reports Q1 Net Profit jump of 42% YOY driven by international exports",
    source: "Livemint",
    time: "1h ago",
    sentiment: "POSITIVE",
    ticker: "POLYCAB",
    summary: "Wire & Cable revenue expands 28% while EBITDA margins improve 180 bps."
  },
  {
    id: 4,
    title: "SEBI publishes revised margin guidelines for algorithmic & high-frequency derivatives trading",
    source: "SEBI Circular",
    time: "2h ago",
    sentiment: "NEUTRAL",
    ticker: "NIFTY",
    summary: "Risk management framework updated to prevent flash crashes during high volatility events."
  }
];

const DEFAULT_NOTIFICATIONS = [
  {
    id: 1,
    title: "Price Alert Triggered",
    symbol: "RELIANCE",
    msg: "RELIANCE crossed ₹2,950 (+2.45% breakout)",
    time: "5m ago",
    type: "bullish"
  },
  {
    id: 2,
    title: "AI Screener Opportunity",
    symbol: "POLYCAB",
    msg: "Polycab achieved Multibagger Score of 94/100",
    time: "18m ago",
    type: "bullish"
  },
  {
    id: 3,
    title: "Earnings Beat Signal",
    symbol: "TCS",
    msg: "TCS Q1 Net Margin beats consensus estimates by 120 bps",
    time: "40m ago",
    type: "info"
  }
];

export function initNewsAndNotifications() {
  window.openNewsModal = openNewsModal;
  window.closeNewsModal = closeNewsModal;
  window.openNotificationsModal = openNotificationsModal;
  window.closeNotificationsModal = closeNotificationsModal;
  window.openShortcutsModal = openShortcutsModal;
  window.closeShortcutsModal = closeShortcutsModal;

  renderNewsFeed();
  renderNotificationsFeed();
}

export function openNewsModal() {
  const overlay = document.getElementById("news-modal-overlay");
  if (overlay) overlay.classList.add("active");
}

export function closeNewsModal() {
  const overlay = document.getElementById("news-modal-overlay");
  if (overlay) overlay.classList.remove("active");
}

export function openNotificationsModal() {
  const overlay = document.getElementById("notifications-modal-overlay");
  if (overlay) overlay.classList.add("active");
}

export function closeNotificationsModal() {
  const overlay = document.getElementById("notifications-modal-overlay");
  if (overlay) overlay.classList.remove("active");
}

export function openShortcutsModal() {
  const overlay = document.getElementById("shortcuts-modal-overlay");
  if (overlay) overlay.classList.add("active");
}

export function closeShortcutsModal() {
  const overlay = document.getElementById("shortcuts-modal-overlay");
  if (overlay) overlay.classList.remove("active");
}

function renderNewsFeed() {
  const container = document.getElementById("news-feed-container");
  if (!container) return;

  const newsHTML = DEFAULT_NEWS.map(item => {
    let sentimentBadge = `<span class="sentiment-badge sentiment-positive">▲ Positive</span>`;
    if (item.sentiment === "NEGATIVE") sentimentBadge = `<span class="sentiment-badge sentiment-negative">▼ Negative</span>`;
    if (item.sentiment === "NEUTRAL") sentimentBadge = `<span class="sentiment-badge sentiment-neutral">■ Neutral</span>`;

    return `
      <div class="p-3 bg-surface-lowest rounded border border-surface-border space-y-1.5 hover:border-gold/50 transition-colors">
        <div class="flex justify-between items-center text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="font-bold text-cream-dark bg-gold/20 px-2 py-0.5 rounded cursor-pointer" onclick="closeNewsModal(); window.selectSymbol('${item.ticker}')">$${item.ticker}</span>
            <span class="text-muted text-[11px]">${item.source} • ${item.time}</span>
          </div>
          ${sentimentBadge}
        </div>
        <h4 class="font-serif font-bold text-sm text-cream-dark leading-snug cursor-pointer hover:text-gold" onclick="closeNewsModal(); window.selectSymbol('${item.ticker}')">${item.title}</h4>
        <p class="text-xs text-cream-muted leading-relaxed">${item.summary}</p>
      </div>
    `;
  }).join("");

  container.innerHTML = newsHTML;
}

function renderNotificationsFeed() {
  const container = document.getElementById("notifications-list-container");
  if (!container) return;

  const notifHTML = DEFAULT_NOTIFICATIONS.map(n => `
    <div class="p-2.5 bg-surface-lowest rounded border border-surface-border flex items-start gap-2 text-xs hover:border-gold/40 cursor-pointer"
         onclick="closeNotificationsModal(); window.selectSymbol('${n.symbol}')">
      <span class="material-symbols-outlined text-gold text-base">notifications_active</span>
      <div class="flex-1 space-y-0.5">
        <div class="flex justify-between items-center font-mono">
          <span class="font-bold text-gold">${n.title} (${n.symbol})</span>
          <span class="text-[10px] text-muted">${n.time}</span>
        </div>
        <p class="text-gray-200">${n.msg}</p>
      </div>
    </div>
  `).join("");

  container.innerHTML = notifHTML;
}
