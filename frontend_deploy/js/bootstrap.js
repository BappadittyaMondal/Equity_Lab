// bootstrap.js – loads panel modules and initializes app
import { renderConvictionPanel } from "./conviction_panel.js";
import { renderWatchlistPanel } from "./watchlist_panel.js";
import { renderScorecardPanel } from "./scorecard_panel.js";
import { renderCAGRMatrixPanel } from "./cagr_matrix_panel.js";
import { renderSwingAlertsPanel } from "./swing_alerts_panel.js";
import { renderDriftStatusIndicator } from "./drift_panel.js";
import { renderMultibaggerPanel } from "./multibagger_panel.js";
import { renderProbabilityPanel } from "./probability_panel.js";
import { renderComparePanel } from "./compare_panel.js";
import { renderTimelinePanel } from "./timeline_panel.js";
import { renderThesisPanel } from "./thesis_panel.js";
import { renderLifecyclePanel } from "./lifecycle_panel.js";
import { initHeaderNav } from "./header_nav.js";
import { initSidebar } from "./sidebar_nav.js";
import { initMobileDrawer } from "./mobile_drawer.js";
import { initAiDock } from "./aiassistant_dock.js";
import { initMainCanvas } from "./main_canvas.js";
import { initFooter } from "./footer.js";
import { initApiHealth, loadTickerStrip, loadRegimeData, loadStrategyCatalog, fetchAndRenderChart, loadWatchlist } from "./api.js";

/**
 * Global Symbol Selector — Updates all research panels simultaneously for selected ticker.
 * @param {string} symbol - Ticker symbol (e.g. RELIANCE, TCS, INFY)
 */
export function selectSymbol(symbol) {
  if (!symbol) return;
  const cleanSymbol = symbol.trim().toUpperCase();
  window.__IERL_SELECTED_SYMBOL = cleanSymbol;

  // Ensure view is set to command center so panels are visible
  if (typeof window.switchView === "function") {
    window.switchView("command");
  }

  // Update all ticker-dependent panels
  renderConvictionPanel(cleanSymbol);
  renderScorecardPanel(cleanSymbol);
  renderCAGRMatrixPanel(cleanSymbol);
  renderThesisPanel(cleanSymbol);
  renderLifecyclePanel(cleanSymbol);
  renderTimelinePanel(cleanSymbol);
  fetchAndRenderChart("1y");

  // Smooth scroll to top of main canvas
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Expose globally
window.selectSymbol = selectSymbol;
window.selectWatchlistSymbol = selectSymbol;

async function initApp() {
  await initHeaderNav();
  initSidebar();
  initMobileDrawer();
  initAiDock();
  initMainCanvas();
  initFooter();

  // basic startup actions
  initApiHealth();
  renderDriftStatusIndicator();
  loadTickerStrip();
  loadRegimeData();
  loadStrategyCatalog();
  fetchAndRenderChart("1y");
  loadWatchlist();
  renderWatchlistPanel();
  renderSwingAlertsPanel();
  renderMultibaggerPanel();
  renderProbabilityPanel();
  renderComparePanel(["RELIANCE", "TCS", "INFY"]);

  // Selected symbol rendering
  const urlParams = new URLSearchParams(window.location.search);
  const sym = urlParams.get('symbol') || window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  selectSymbol(sym);
}

document.addEventListener("DOMContentLoaded", initApp);
