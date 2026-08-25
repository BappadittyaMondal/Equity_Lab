/**
 * watchlist_panel.js — Strategy Watchlist System (watchlist_500) for StockAnalyzer
 * Manages up to 500 equities categorized by Multibagger, Swing, SIP, Turnaround, and Custom lists.
 */import { selectSymbol } from "./main_canvas.js";
import { apiFetch } from "./api.js";

const DEFAULT_WATCHLIST = [
  { symbol: "RELIANCE", name: "Reliance Industries", price: 2980, chg: 2.45, score: 92, risk: "Low", category: "Multibagger" },
  { symbol: "TCS", name: "Tata Consultancy Services", price: 4250, chg: -0.65, score: 95, risk: "Low", category: "SIP" },
  { symbol: "HDFCBANK", name: "HDFC Bank Ltd", price: 1640, chg: 1.15, score: 91, risk: "Low", category: "SIP" },
  { symbol: "INFY", name: "Infosys Ltd", price: 1860, chg: -0.30, score: 88, risk: "Low", category: "SIP" },
  { symbol: "POLYCAB", name: "Polycab India Ltd", price: 6850, chg: 4.10, score: 94, risk: "Med", category: "Multibagger" },
  { symbol: "HAL", name: "Hindustan Aeronautics", price: 4680, chg: 3.20, score: 93, risk: "Med", category: "Swing" },
  { symbol: "BHEL", name: "Bharat Heavy Electricals", price: 295, chg: 5.80, score: 87, risk: "High", category: "Swing" },
  { symbol: "SUZLON", name: "Suzlon Energy Ltd", price: 78, chg: 4.90, score: 82, risk: "High", category: "Turnaround" },
  { symbol: "TRENT", name: "Trent Ltd", price: 7100, chg: 2.90, score: 90, risk: "Med", category: "Multibagger" },
  { symbol: "DIXON", name: "Dixon Technologies", price: 12400, chg: 1.85, score: 89, risk: "Med", category: "Multibagger" },
];

export async function renderWatchlistPanel() {
  const container = document.getElementById("watchlist-body");
  if (!container) return;

  window.__IERL_WATCHLIST_DATA = window.__IERL_WATCHLIST_DATA || DEFAULT_WATCHLIST;
  window.filterWatchlistCategory = filterWatchlistCategory;
  window.addSymbolToWatchlist = addSymbolToWatchlist;

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <!-- Strategy Category Tabs -->
      <div class="tab-bar">
        <button class="tab-btn active" data-cat="ALL" onclick="window.filterWatchlistCategory('ALL')">All (500)</button>
        <button class="tab-btn" data-cat="Multibagger" onclick="window.filterWatchlistCategory('Multibagger')">🚀 Multibagger</button>
        <button class="tab-btn" data-cat="SIP" onclick="window.filterWatchlistCategory('SIP')">💎 SIP</button>
        <button class="tab-btn" data-cat="Swing" onclick="window.filterWatchlistCategory('Swing')">⚡ Swing</button>
        <button class="tab-btn" data-cat="Turnaround" onclick="window.filterWatchlistCategory('Turnaround')">🔄 Turnaround</button>
      </div>

      <!-- Quick Add Symbol Input Bar -->
      <div class="flex items-center gap-2">
        <input type="text" id="watchlist-add-input" class="form-input text-xs" placeholder="Add Ticker to Watchlist (e.g., KEI)..." />
        <button onclick="window.addSymbolFromInput()" class="btn-primary text-xs px-3 py-1.5 whitespace-nowrap">+ Add</button>
      </div>

      <!-- Table of Equities -->
      <div class="flex-1 overflow-x-auto" id="watchlist-table-container"></div>
    </div>
  `;

  window.addSymbolFromInput = () => {
    const input = document.getElementById("watchlist-add-input");
    if (input && input.value.trim()) {
      addSymbolToWatchlist(input.value.trim());
      input.value = "";
    }
  };

  filterWatchlistCategory("ALL");
}

export function filterWatchlistCategory(cat = "ALL") {
  const tabBtns = document.querySelectorAll("#watchlist-window .tab-btn");
  tabBtns.forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-cat") === cat);
  });

  const tableContainer = document.getElementById("watchlist-table-container");
  if (!tableContainer) return;

  const data = window.__IERL_WATCHLIST_DATA || DEFAULT_WATCHLIST;
  const filtered = cat === "ALL" ? data : data.filter(item => item.category === cat);

  const rows = filtered.map(item => {
    const chgColor = item.chg >= 0 ? "text-green font-semibold" : "text-red font-semibold";
    const arrow = item.chg >= 0 ? "▲" : "▼";
    const scoreBadgeClass = item.score >= 90 ? "badge-success" : item.score >= 80 ? "badge-warning" : "badge-neutral";

    return `
      <tr class="border-b border-surface-border/40 hover:bg-surface-high/60 transition-colors cursor-pointer" onclick="window.selectSymbol('${item.symbol}')">
        <td class="py-2 px-3 font-mono font-bold text-gold text-xs">${item.symbol}</td>
        <td class="py-2 px-3 text-xs font-mono text-white">₹${item.price.toLocaleString("en-IN")}</td>
        <td class="py-2 px-3 text-xs font-mono ${chgColor}">${arrow} ${item.chg.toFixed(2)}%</td>
        <td class="py-2 px-3 text-xs text-right">
          <span class="badge ${scoreBadgeClass}">${item.score} Conviction</span>
        </td>
      </tr>
    `;
  }).join("");

  tableContainer.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Price</th>
          <th>Change</th>
          <th class="text-right">Conviction Level</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

export async function addSymbolToWatchlist(symbol, category = "Multibagger") {
  if (!symbol) return;
  const cleanSym = symbol.trim().toUpperCase().replace(".NS", "").replace(".BO", "");
  
  window.__IERL_WATCHLIST_DATA = window.__IERL_WATCHLIST_DATA || DEFAULT_WATCHLIST;
  
  if (window.__IERL_WATCHLIST_DATA.some(i => i.symbol === cleanSym)) {
    filterWatchlistCategory("ALL");
    return;
  }

  let realPrice = 1500;
  let realChg = 0.0;
  let realScore = 85;

  try {
    const qResp = await apiFetch(`/api/v1/ticker/${encodeURIComponent(cleanSym)}`);
    if (qResp.ok) {
      const qData = await qResp.json();
      if (qData && qData.price) {
        realPrice = qData.price;
        realChg = qData.change_percent || 0.0;
      }
    }
  } catch (_) {}

  try {
    const sResp = await apiFetch(`/api/v1/research/scorecard?symbol=${encodeURIComponent(cleanSym)}`);
    if (sResp.ok) {
      const sData = await sResp.json();
      if (sData && sData.scores && sData.scores.overall_score) {
        realScore = sData.scores.overall_score;
      }
    }
  } catch (_) {} }
  } catch (_) {}

  window.__IERL_WATCHLIST_DATA.unshift({
    symbol: cleanSym,
    name: cleanSym,
    price: realPrice,
    chg: realChg,
    score: realScore,
    risk: "Med",
    category
  });

  filterWatchlistCategory("ALL");
}
