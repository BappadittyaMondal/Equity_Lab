/**
 * bootstrap.js — Master Application Bootstrapper for StockAnalyzer Dashboard
 * Orchestrates multi-window layout engine, header toolbar, central charting hub,
 * AI Stock Chat, strategy finders, watchlist_500 system, and keyboard shortcuts.
 */

import { windowManager } from "./window_manager.js";
import { initHeaderNav } from "./header_nav.js";
import { initMainCanvas, selectSymbol } from "./main_canvas.js";
import { renderConvictionPanel } from "./conviction_panel.js";
import { renderScorecardPanel } from "./scorecard_panel.js";
import { initAiDock } from "./aiassistant_dock.js";
import { initCommunityFeed } from "./community_feed.js";
import { renderMultibaggerPanel } from "./multibagger_panel.js";
import { renderWatchlistPanel } from "./watchlist_panel.js";
import { initNewsAndNotifications, closeNewsModal, closeNotificationsModal, closeShortcutsModal, openShortcutsModal } from "./news_notifications.js";
import { initApiHealth, loadTickerStrip } from "./api.js";

import { renderMIVSScorecardPanel } from "./mivs_scorecard_panel.js";
import { renderGrowthMarketGapPanel } from "./growth_market_gap_panel.js";
import { initFooter } from "./footer.js";

async function initApp() {
  // 1. Load Header Component
  try {
    await initHeaderNav();
  } catch (e) {
    console.error("Header nav load non-critical error:", e);
  }

  // 2. Initialize Multi-Window Manager Engine
  windowManager.init();
  window.saveWorkspaceLayout = () => windowManager.saveLayout();
  window.resetWorkspaceLayout = () => windowManager.resetLayout();

  // 3. Initialize Panels & Engines
  initMainCanvas();
  initAiDock();
  initCommunityFeed();
  renderMultibaggerPanel();
  renderWatchlistPanel();
  initNewsAndNotifications();
  initFooter();

  // Initial Scorecard rendering
  renderConvictionPanel("RELIANCE");
  renderScorecardPanel("RELIANCE");
  renderGrowthMarketGapPanel("RELIANCE");
  renderMIVSScorecardPanel("mivs-scorecard-panel", "RELIANCE");

  // Live Ticker Tape & Health
  initApiHealth();
  loadTickerStrip();
  setInterval(loadTickerStrip, 15000); // 15s refresh cycle

  // 4. Keyboard Shortcuts Global Event Listener
  setupKeyboardShortcuts();

  // 5. Expose global helpers
  window.selectSymbol = (sym) => {
    selectSymbol(sym);
    renderConvictionPanel(sym);
    renderScorecardPanel(sym);
    renderGrowthMarketGapPanel(sym);
    renderMIVSScorecardPanel("mivs-scorecard-panel", sym);
  };
}

function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Esc key: Close modals
    if (e.key === "Escape") {
      closeNewsModal();
      closeNotificationsModal();
      closeShortcutsModal();
    }

    // Don't intercept shortcuts if user is typing inside an input/textarea
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
      return;
    }

    // Alt + Enter: Maximize active focused window
    if (e.altKey && e.key === "Enter") {
      e.preventDefault();
      windowManager.maximizeActiveWindow();
    }

    // Ctrl + S: Save layout
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      windowManager.saveLayout();
      alert("Workspace layout saved successfully!");
    }

    // Forward Slash (/): Focus Quick Search Input
    if (e.key === "/") {
      e.preventDefault();
      const searchInput = document.getElementById("header-search-input");
      if (searchInput) searchInput.focus();
    }

    // Question Mark (?): Open Shortcuts Help Modal
    if (e.key === "?") {
      e.preventDefault();
      openShortcutsModal();
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
