// bootstrap.js – loads panel modules and initializes app
import { renderConvictionPanel } from "./conviction_panel.js";
import { renderWatchlistPanel } from "./watchlist_panel.js";
import { renderScorecardPanel } from "./scorecard_panel.js";
import { renderCAGRMatrixPanel } from "./cagr_matrix_panel.js";
import { renderSwingAlertsPanel } from "./swing_alerts_panel.js";
import { renderDriftStatusIndicator } from "./drift_panel.js";
import { renderMultibaggerPanel } from "./multibagger_panel.js";
import { renderProbabilityPanel } from "./probability_panel.js";
import { initHeaderNav } from "./header_nav.js";
import { initSidebar } from "./sidebar_nav.js";
import { initMobileDrawer } from "./mobile_drawer.js";
import { initAiDock } from "./aiassistant_dock.js";
import { initMainCanvas } from "./main_canvas.js";
import { initFooter } from "./footer.js";
import { initApiHealth, loadTickerStrip, loadRegimeData, loadStrategyCatalog, fetchAndRenderChart, loadWatchlist } from "./api.js";

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

  // Selected symbol rendering
  const urlParams = new URLSearchParams(window.location.search);
  const sym = urlParams.get('symbol') || window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  renderConvictionPanel(sym);
  renderScorecardPanel(sym);
  renderCAGRMatrixPanel(sym);
}

document.addEventListener("DOMContentLoaded", initApp);
