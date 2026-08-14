---
name: Obsidian Aurum
colors:
  surface: '#18120d'
  surface-dim: '#18120d'
  surface-bright: '#403832'
  surface-container-lowest: '#130d09'
  surface-container-low: '#211a15'
  surface-container: '#1e2024'
  surface-container-high: '#302923'
  surface-container-highest: '#3b332e'
  on-surface: '#eee0d7'
  on-surface-variant: '#d8c3b4'
  inverse-surface: '#eee0d7'
  inverse-on-surface: '#372f29'
  outline: '#a08d80'
  outline-variant: '#524439'
  surface-tint: '#ffb77b'
  primary: '#ffb77b'
  on-primary: '#4d2700'
  primary-container: '#c8803f'
  on-primary-container: '#432100'
  inverse-primary: '#8c4f10'
  secondary: '#e9c349'
  on-secondary: '#3c2f00'
  secondary-container: '#af8d11'
  on-secondary-container: '#342800'
  tertiary: '#74d4ea'
  on-tertiary: '#00363f'
  tertiary-container: '#359db2'
  on-tertiary-container: '#002f37'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdcc2'
  primary-fixed-dim: '#ffb77b'
  on-primary-fixed: '#2e1500'
  on-primary-fixed-variant: '#6d3a00'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#a8edff'
  tertiary-fixed-dim: '#74d4ea'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5b'
  background: '#18120d'
  on-background: '#eee0d7'
  surface-variant: '#3b332e'
  obsidian-bg: '#111318'
  brushed-gold: '#d4af37'
  deep-copper: '#b87333'
  bullish-green: '#4edea3'
  bearish-red: '#ffb4ab'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-table:
    fontFamily: IBM Plex Mono
    fontSize: 13px
    fontWeight: '450'
    lineHeight: 18px
  data-label:
    fontFamily: IBM Plex Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base-unit: 4px
  gutter: 16px
  margin-desktop: 24px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system evolves from a purely technical terminal into an **Elite Financial Intelligence** platform. It targets institutional investors and high-net-worth analysts who demand both precision and a sense of exclusive, high-value insight. The brand personality is **Prestigious, Technical, and Indisputable.**

The design style is **Modern Corporate with Metallic Accents**. It leverages the "Dark Terminal" foundation of the previous system but infuses it with a high-contrast, premium aesthetic. By replacing sterile blues with warm coppers and brushed golds, the UI shifts from "utility software" to a "private wealth instrument." Structural integrity is maintained through rigid grids, while the metallic palette creates a psychological association with tangible value and market-moving intelligence.

## Colors

The palette is anchored in a deep **Obsidian (#111318)** background to ensure maximum legibility for financial data and to allow the new metallic accents to gleam without visual noise.

- **Primary (Deep Copper - #b87333):** Used for primary action buttons, active navigational states, and structural highlights that require the most visual weight.
- **Secondary (Brushed Gold - #d4af37):** Applied to icons, secondary accents, and subtle decorative borders. It serves as a "high-light" to the deeper copper.
- **Semantic Indicators:** Functional colors remain strictly utility-focused. **Bullish Green (#4edea3)** and **Bearish Red (#ffb4ab)** are preserved for market directionality, ensuring that critical data signals are never confused with brand accents.
- **Neutral Palette:** Neutral grays and charcoals are slightly warmed to complement the copper/gold theme, moving away from cool-blue grays to a more balanced, "charred oak" neutral scale.

## Typography

This design system maintains a disciplined dual-font strategy to balance editorial clarity with data density.

1. **Inter (Interface & Narrative):** The workhorse for all navigational elements, section headers, and qualitative analytical text. It is clean, modern, and provides an approachable contrast to the dense financial data.
2. **IBM Plex Mono (Quantitative Data):** Every number, ticker symbol, and spreadsheet cell must use this font. Its monospaced nature is non-negotiable for comparing rows of figures, ensuring that decimal points and currency symbols align vertically for rapid scanning.

**Emphasis Rules:**
- **Copper Highlights:** Use the primary copper color for key "Decision Labels" in Inter Bold.
- **Gold Accents:** Use the brushed gold for "Label-Data" (e.g., metric units or status tags) to differentiate units from the raw numbers.

## Layout & Spacing

The layout is a **Rigid Terminal Grid** designed to maximize "above-the-fold" information density. It utilizes a 12-column grid system that prioritizes vertical alignment over fluid expansion.

- **Grid Logic:** On desktop, a 12-column grid with 16px gutters is used. Margins are fixed at 24px to create a contained, "instrument panel" feel.
- **Responsive Behavior:** The grid collapses to 4 columns on mobile. In mobile views, data-heavy tables should be replaced with vertical "Summary Cards" or use horizontal overflow with locked "Ticker" columns.
- **Rhythm:** All spacing is derived from a 4px base unit. Component heights (buttons, inputs) are strictly standardized to maintain a horizontal baseline across the dashboard.

## Elevation & Depth

Depth is conveyed through **Tonal Tiering and Metallic Strokes** rather than traditional shadows, which can muddy a dark interface.

- **The Z-Axis:**
  - **Level 0 (Canvas):** #111318 (Pure Obsidian).
  - **Level 1 (Surface):** #1e2024. Used for the primary content cards and data containers.
  - **Level 2 (Popovers):** #282a2e. Used for dropdowns and tooltips.
- **Metallic Outlines:** To elevate components, use 1px "Ghost Borders." Instead of flat grays, these borders use a low-opacity copper (#b87333) to suggest a physical, metallic frame.
- **Focus States:** Active inputs or focused cards use a 1px solid Brushed Gold border with a 4px soft outer glow (rgba(212, 175, 55, 0.15)) to simulate light reflecting off a metal edge.

## Shapes

The shape language is **Technical and Precision-Driven.** 

- **Soft (4px):** This is the default for buttons, input fields, and standard cards. It removes the "aggressive" edge of a pure terminal while remaining professional and efficient.
- **Sharp (0px):** Used for internal tabs, segmented controls, and dashboard widgets that sit flush against one another. This emphasizes the "modular" and "interlocking" nature of the data.
- **Pill (Full):** Reserved exclusively for status badges (e.g., "Active," "Pending") and small Ticker tags to make them instantly recognizable as distinct entities from the square data cells.

## Components

- **Buttons:** 
  - **Primary:** Solid Deep Copper (#b87333) with high-contrast text. 
  - **Secondary:** Outlined with 1px Brushed Gold (#d4af37). 
  - **Ghost:** No background, Brushed Gold text for low-priority dashboard actions.
- **Data Grids:** Rows use a subtle hover highlight of #282a2e. Vertical dividers are avoided; use thin horizontal rules in #333539. The header row should have a subtle 1px copper bottom-border.
- **Input Fields:** Background matches the Obsidian canvas (#111318). Borders are #424754, shifting to Brushed Gold on focus.
- **Chips & Badges:** Tickers ($AAPL, $BTC) use a sharp 2px radius and a dark-gray background. Bullish/Bearish indicators use semantic colors with 15% opacity fills.
- **Cards:** Level 1 Surface color. Headers are distinguished by a subtle top-border in Deep Copper (2px height) to anchor the eye.
- **AI/Intelligence Panels:** To differentiate AI-generated summaries from raw data, use a subtle Brushed Gold linear-gradient border and a backdrop blur of 8px.