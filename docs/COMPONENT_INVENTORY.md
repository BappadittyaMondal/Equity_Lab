# Component Inventory — Equity Lab OS UI Panel Architecture

> **UI ARCHITECTURE FREEZE**: Documents the 10 core institutional UI panel components actively mounted in `frontend_deploy/index.html` and controlled by `main_canvas.js` and `sidebar_nav.js`.

## 1. UI Panel Component Inventory

| Component ID | Panel Name | Source Component File | Backend API Endpoint Wiring | Key Features & Output Display |
| :--- | :--- | :--- | :--- | :--- |
| `scorecard-panel` | Institutional Equity Scorecard | `components/scorecard_panel.js` | `/api/v1/research/scorecard` | 5-pillar fundamental scorecard, ROIC, Beneish M-Score, Altman Z |
| `cagr-matrix-panel` | Multi-Period CAGR Matrix | `components/cagr_matrix_panel.js` | `/api/v1/research/cagr-matrix` | 1Y, 3Y, 5Y Revenue, EBITDA, PAT, & EPS growth matrix |
| `thesis-panel` | Bayesian Thesis Monitor | `components/thesis_panel.js` | `/api/v1/data/thesis/{symbol}` | Growth drivers, catalysts, risks, & invalidation conditions |
| `lifecycle-panel` | Business Lifecycle Stage | `components/lifecycle_panel.js` | `/api/v1/data/lifecycle/{symbol}` | 10-stage lifecycle classifier & transition rationale |
| `timeline-panel` | Point-in-Time Timeline | `components/timeline_panel.js` | `/api/v1/data/companies/{sym}/timeline` | Chronological audit trail of filings, events, & corporate actions |
| `compare-panel` | Multi-Ticker Comparison | `components/compare_panel.js` | `/api/v1/compare` | Peer comparison matrix across valuation & growth metrics |
| `swing-alerts-panel` | Technical Swing Breakout Alerts | `components/swing_alerts_panel.js` | `/api/v1/strategies/swing-alerts` | VCP contraction, pocket pivot, & RS rating breakout signals |
| `watchlist-panel` | Conviction Watchlist | `components/watchlist_panel.js` | `/api/v1/watchlist` | Active portfolio watchlist with target prices & quick notes |
| `probability-panel` | Return Probability Engine | `components/probability_panel.js` | `/api/v1/return-probability` | Empirical Monte Carlo & historical probability return curves |
| `conviction-panel` | Conviction Decision Engine | `components/conviction_panel.js` | `/api/v1/decision/{symbol}` | Multi-factor conviction score (0-100), verdict, & bull/bear debate |

---

## 2. Navigation & View Switcher Integration

All 10 panels are mounted as dynamic view panes inside `#main-canvas-content` and managed by `sidebar_nav.js`:

```javascript
// Sidebar navigation view switcher dispatch
function switchView(viewId) {
    const panels = document.querySelectorAll('.ui-panel-view');
    panels.forEach(p => p.classList.add('hidden'));
    
    const targetPanel = document.getElementById(viewId);
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
        triggerPanelRefresh(viewId);
    }
}
```

---

## 3. Aesthetic Design Standards Compliance

- **Design Tokens**: Obsidian Aurum color palette (`#0B0E14` obsidian background, `#D4AF37` metallic gold accents, `#1E222D` card fills).
- **Typography**: Google Fonts Inter & Outfit.
- **Component Styling**: Micro-animations (`transition: all 0.25s ease`), glassmorphism cards (`backdrop-filter: blur(8px)`).

---

## 4. Backend-Only Endpoints (not yet in UI)

The following backend endpoints are high-performance analytical engines operational via direct REST API and SDK calls. UI exposure is planned for the v1.1 dashboard expansion release:

1. `/api/v1/data/custom-screen` — Dynamic Universal AST Custom Screener Engine (`POST /api/v1/data/custom-screen`). Reason: Serves programmatic AST query DSL callers; UI query builder scheduled for v1.1.
2. `/api/v1/multibagger/institutional-rank` — Universal 27-Engine Multibagger Ranker (`POST /api/v1/multibagger/institutional-rank`). Reason: High-throughput batch calculation engine consumed by background schedulers and CLI reports; UI grid view targeted for v1.1.
3. `/api/v1/multibagger/institutional-score/{symbol}` — Single-Stock 27-Engine Scorecard (`GET /api/v1/multibagger/institutional-score/{symbol}`). Reason: Deep vector breakdown consumed by automated reporting pipelines; modal UI inspector scheduled for v1.1.

