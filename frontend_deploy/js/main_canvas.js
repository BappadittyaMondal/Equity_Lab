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

  // Inject additional view containers if not already in index.html
  const extraPanels = [
    { id: "ticker-strip-container", html: `<section id="ticker-strip-container" class="mb-4"><div class="ticker-strip-wrapper bg-surface-low rounded border border-surface-border/50 py-2 px-3"><div id="ticker-strip"></div></div></section>` },
    { id: "regime-panel", html: `<section id="regime-panel" class="mb-4"></section>` },
    { id: "chart-panel", html: `<section id="chart-panel" class="mb-6"></section>` },
    { id: "strategy-catalog-container", html: `<section id="strategy-catalog-container" class="view-panel mb-6" data-view="strategies"><div class="p-6 bg-surface-lowest rounded-xl border"><h3 class="text-lg font-bold text-gold mb-4">Strategy Screening Engine</h3><div id="strategy-catalog"></div></div></section>` },
  ];

  for (const panel of extraPanels) {
    if (!document.getElementById(panel.id)) {
      canvas.insertAdjacentHTML("afterbegin", panel.html);
    }
  }

  // Default view: command (shows conviction + watchlist + chart + analysis)
  switchView("command");
}

/**
 * Switch between views. Shows/hides view-specific panels cleanly.
 * @param {string} viewName - View identifier (command, multibagger, compare, probability, strategies, aiassistant)
 */
export function switchView(viewName) {
  const commandPanels = [
    "conviction-panel",
    "scorecard-panel",
    "cagr-matrix-panel",
    "thesis-panel",
    "lifecycle-panel",
    "timeline-panel",
    "watchlist-panel",
    "swing-alerts-panel",
    "chart-panel",
    "ticker-strip-container",
    "regime-panel"
  ];

  const viewMap = {
    "command": commandPanels,
    "multibagger": ["multibagger-screener-panel", "ticker-strip-container"],
    "compare": ["compare-panel", "ticker-strip-container"],
    "probability": ["probability-panel", "ticker-strip-container"],
    "strategies": ["strategy-catalog-container", "swing-alerts-panel", "ticker-strip-container"],
    "options": ["conviction-panel", "ticker-strip-container"]
  };

  const activeIds = viewMap[viewName] || commandPanels;

  // All known main canvas section IDs
  const allSectionIds = [
    "conviction-panel",
    "scorecard-panel",
    "cagr-matrix-panel",
    "thesis-panel",
    "lifecycle-panel",
    "timeline-panel",
    "compare-panel",
    "swing-alerts-panel",
    "multibagger-screener-panel",
    "probability-panel",
    "watchlist-panel",
    "chart-panel",
    "ticker-strip-container",
    "regime-panel",
    "strategy-catalog-container"
  ];

  allSectionIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = activeIds.includes(id) ? "" : "none";
    }
  });

  // Toggle AI dock visibility for ai assistant view
  const aiDock = document.getElementById("aiassistant-dock");
  if (aiDock && viewName === "aiassistant") {
    aiDock.style.display = "flex";
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}
