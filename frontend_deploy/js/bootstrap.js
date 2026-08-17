// bootstrap.js – loads panel modules and initializes app
import { renderConvictionPanel } from "./conviction_panel.js";
import { renderWatchlistPanel } from "./watchlist_panel.js";
import { initHeaderNav } from "./header_nav.js";
import { initSidebar } from "./sidebar_nav.js";
import { initMobileDrawer } from "./mobile_drawer.js";
import { initAiDock } from "./aiassistant_dock.js";
import { initMainCanvas } from "./main_canvas.js";
import { initFooter } from "./footer.js";
import { initApiHealth, loadTickerStrip, loadRegimeData, loadStrategyCatalog, fetchAndRenderChart, loadWatchlist } from "./api.js";

function initApp() {
  initHeaderNav();
  initSidebar();
  initMobileDrawer();
  initAiDock();
  initMainCanvas();
  initFooter();
  // basic startup actions
  initApiHealth();
  loadTickerStrip();
  loadRegimeData();
  loadStrategyCatalog();
  fetchAndRenderChart("1y");
  loadWatchlist();
  renderWatchlistPanel();
  // If a symbol is provided via query param, render its conviction panel
  const urlParams = new URLSearchParams(window.location.search);
  const sym = urlParams.get('symbol');
  if (sym) {
    renderConvictionPanel(sym);
  }
}

document.addEventListener("DOMContentLoaded", initApp);
