// main_canvas.js — Main content area initialization and view switching
// Manages the central canvas where research panels are rendered

/**
 * Initialize the main canvas with default view panels and view-switching logic.
 */
export function initMainCanvas() {
  const canvas = document.getElementById("main-canvas");
  if (!canvas) return;

  // Expose switchView globally so sidebar buttons can call it
  window.switchView = switchView;

  // Set default selected symbol
  window.__IERL_SELECTED_SYMBOL = window.__IERL_SELECTED_SYMBOL || "RELIANCE";

  // Ensure panels exist for each view (add them after existing conviction/watchlist panels)
  const viewPanels = [
    { id: "ticker-strip-container", html: `<section id="ticker-strip-container" class="mb-4"><div class="ticker-strip-wrapper bg-surface-low rounded border border-surface-border/50 py-2 px-3"><div id="ticker-strip"></div></div></section>` },
    { id: "regime-panel", html: `<section id="regime-panel" class="mb-4"></section>` },
    { id: "chart-panel", html: `<section id="chart-panel" class="mb-6"></section>` },
    { id: "strategy-catalog-container", html: `<section id="strategy-catalog-container" class="view-panel mb-6" data-view="strategies"><div class="p-6 bg-surface-lowest rounded-xl border"><h3 class="text-lg font-bold text-gold mb-4">Strategy Screening Engine</h3><div id="strategy-catalog"></div></div></section>` },
    { id: "compare-container", html: `<section id="compare-container" class="view-panel mb-6" data-view="compare"><div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted"><span class="material-symbols-outlined text-3xl mb-2 text-gold block">compare_arrows</span><h3 class="text-sm font-semibold text-gold">Stock Comparison</h3><p class="text-xs mt-1">Select 2–5 stocks to compare fundamentals, technicals, and conviction scores.</p></div></section>` },
    { id: "probability-container", html: `<section id="probability-container" class="view-panel mb-6" data-view="probability"><div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted"><span class="material-symbols-outlined text-3xl mb-2 text-gold block">query_stats</span><h3 class="text-sm font-semibold text-gold">Return Probability Engine</h3><p class="text-xs mt-1">Estimate forward return probabilities using historical empirical distributions.</p></div></section>` },
    { id: "multibagger-container", html: `<section id="multibagger-container" class="view-panel mb-6" data-view="multibagger"><div class="p-6 bg-surface-lowest rounded-xl border text-center text-muted"><span class="material-symbols-outlined text-3xl mb-2 text-gold block">rocket_launch</span><h3 class="text-sm font-semibold text-gold">Multibagger Screener</h3><p class="text-xs mt-1">Identify early-stage growth inflection candidates across NSE universe.</p></div></section>` },
  ];

  for (const panel of viewPanels) {
    if (!document.getElementById(panel.id)) {
      canvas.insertAdjacentHTML("beforeend", panel.html);
    }
  }

  // Default view: command (shows conviction + watchlist + chart)
  switchView("command");
}

/**
 * Switch between views. Shows/hides view-specific panels.
 * @param {string} viewName - View identifier (command, multibagger, compare, probability, strategies, aiassistant)
 */
function switchView(viewName) {
  // Hide all view-specific panels
  document.querySelectorAll(".view-panel").forEach(el => {
    el.style.display = "none";
  });

  // Core panels (conviction + watchlist + chart) visible only in command view
  const corePanels = ["conviction-panel", "watchlist-panel", "chart-panel", "ticker-strip-container", "regime-panel"];
  corePanels.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = viewName === "command" ? "" : "none";
  });

  // Show the selected view panel
  if (viewName !== "command") {
    const targetPanel = document.querySelector(`.view-panel[data-view="${viewName}"]`);
    if (targetPanel) {
      targetPanel.style.display = "";
    }
  }

  // Toggle AI dock visibility for ai assistant view on smaller screens
  const aiDock = document.getElementById("aiassistant-dock");
  if (aiDock && viewName === "aiassistant") {
    aiDock.style.display = "flex";
  }

  // Update active sidebar item styling
  document.querySelectorAll("#sidebar-nav button").forEach(btn => {
    btn.classList.remove("border-gold");
  });
}
