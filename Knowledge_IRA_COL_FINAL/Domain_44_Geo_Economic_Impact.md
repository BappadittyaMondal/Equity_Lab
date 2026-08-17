# Domain 44 — Geo-Economic Impact Framework

**Version:** v_0.0
**Status:** Production Ready
**Category:** Knowledge Domain (New)
**Role:** Maps global/macro variables to concrete, sector-specific effects on Indian equities — closes the gap where Domain 13 (Macroeconomic Themes) had generic theory but no India-specific transmission mechanism

---

## Purpose

Domain 13 explains *what* macro forces exist (rate cycles, inflation, currency). This domain explains *which Indian sector moves which way, and why* — the actual transmission mechanism an analyst needs to translate a macro headline into a stock-level view.

---

## 1. USD/INR Movement

| Direction | Sectors Helped | Sectors Hurt | Mechanism |
|---|---|---|---|
| **Rupee depreciates** (INR weakens vs USD) | IT Services, Pharma (generics exporters), Textiles/Garment exporters | Oil Marketing Companies, Aviation, companies with USD-denominated debt, Import-heavy consumer durables | Export revenue is USD-denominated and converts to more rupees; importers pay more rupees for the same USD cost |
| **Rupee appreciates** (INR strengthens vs USD) | Oil Marketing Companies, Aviation, Import-heavy retailers | IT Services, Pharma exporters | Reverse of above |

**Trigger keywords:** "rupee falls," "INR depreciation," "dollar strengthens," "currency impact on IT/pharma"

---

## 2. Crude Oil Price Movement

| Direction | Sectors Helped | Sectors Hurt | Mechanism |
|---|---|---|---|
| **Oil price rises** | Upstream oil producers (ONGC, Oil India), Oil Marketing Companies (if under-recovery is government-absorbed) | Aviation (ATF cost), Paints (crude derivative input), Tyres, Aviation, Logistics/Transport, Fertilizer (subsidy burden) | Direct input cost pass-through; India imports ~85% of crude, so a rise widens the current account deficit too (see Section 4) |
| **Oil price falls** | Aviation, Paints, Tyres, Logistics, Fertilizer, government fiscal position | Upstream oil producers | Reverse of above |

**Trigger keywords:** "crude oil rally," "oil price crash," "OPEC cut," "impact on aviation/paints"

---

## 3. Interest Rate Cycle (RBI Repo Rate)

| Direction | Sectors Helped | Sectors Hurt | Mechanism |
|---|---|---|---|
| **Rate hike cycle** | Banks (near-term NIM expansion on floating-rate loans repricing faster than deposits), Insurance (higher yields on new investments) | Real Estate, NBFCs (borrowing cost up), Auto (EMI-sensitive demand), Capital goods (project financing cost), highly leveraged companies generally | Higher cost of capital compresses margins for borrowers and dampens EMI-driven consumption |
| **Rate cut cycle** | Real Estate, NBFCs, Auto, Capital goods, leveraged companies | Banks (near-term NIM compression until deposit repricing catches up) | Reverse of above |

**Trigger keywords:** "RBI rate hike," "repo rate cut," "impact on NBFC/real estate/banks"

---

## 4. FII/DII Flow Direction

| Direction | Effect | Mechanism |
|---|---|---|
| **FII outflows** | Large-cap, high-free-float stocks fall disproportionately; Rupee tends to weaken simultaneously (compounding Section 1 effects); Mid/small-cap impact is delayed but can be sharper if outflows persist | FIIs hold concentrated positions in large, liquid names; their selling has an outsized index impact |
| **FII inflows** | Large-cap rally leads; often triggers a broader risk-on move into mid/small-caps with a lag | Reverse of above |
| **DII inflows (mutual funds, insurance) offsetting FII outflows** | Cushions the large-cap fall but is usually insufficient to fully offset a sustained FII exit | DII flows are steadier (SIP-driven) but smaller in absolute size during acute FII selling phases |

**Trigger keywords:** "FII selling," "DII buying," "foreign outflows impact," "who is buying when FII sells"

---

## 5. Global Growth / Recession Risk (US/Europe)

| Condition | Sectors Helped | Sectors Hurt | Mechanism |
|---|---|---|---|
| **US/Europe slowdown or recession fear** | Domestic-consumption-focused sectors (FMCG, domestic Pharma, Utilities) — relatively insulated | IT Services (US client budget cuts), export-heavy Textiles, Auto ancillaries with export exposure | IT services revenue is heavily USA/Europe client-budget dependent; discretionary tech spend is often the first cut in a client's downturn |
| **US/Europe strong growth** | IT Services, export-heavy sectors | — | Reverse of above |

**Trigger keywords:** "US recession fear," "IT sector guidance cut," "global slowdown impact on India"

---

## 6. Combining Signals — Worked Example

**Scenario:** Crude oil rises to $95/bbl, rupee simultaneously depreciates to 87/USD, and FIIs are net sellers for the month.

**Analysis using this domain:**
- Crude rise → negative for Aviation, Paints, Tyres (Section 2)
- Rupee depreciation → positive for IT/Pharma exporters, but this partially offsets — not fully cancels — the negative oil/import-cost pressure on oil-import-dependent sectors, since a weaker rupee makes imported crude *even more expensive* in rupee terms (Sections 1 and 2 compound negatively for net oil importers)
- FII selling → compounds rupee weakness (Section 4), and disproportionately hits large-cap financials and IT despite IT's export benefit from Section 1 — the flow effect can temporarily dominate the fundamental currency benefit

**Conclusion pattern:** When multiple macro signals point in different directions for the same sector (as with IT here — helped by rupee, hurt by FII flow and global growth risk), state the conflict explicitly rather than netting it to one answer — this follows Domain 00_Index's Global Conflict Arbitration principle (live/current data and evidence outrank a single theoretical directional call).

---

## 7. Conflict Rule (per 00_Index.md Global Arbitration convention)

This domain's sector-direction table is a **general tendency**, not a deterministic rule. It is always subordinate to:
1. **Company-specific evidence** (Domain 2, 6) — a company's actual hedging policy, debt currency mix, or client concentration can override the sector-general direction stated here.
2. **Governance/Forensic gates** (Domain 8, 24) — a governance or forensic red flag overrides any macro tailwind.

---

## 8. Required Index Update

**Add to `00_Index.md`** table (after Domain 24):

```
| 25 | Geo-Economic Impact Framework | Domain_44_Geo_Economic_Impact.md |
```

**Add to Universal Rules / Cross-Domain Links:** Domain 44 should be auto-linked whenever Domain 1 (Economics) or Domain 13 (Macroeconomic Themes) is triggered, since it's the sector-application layer for both.

---

# Document Information

**Document:** Domain_44_Geo_Economic_Impact.md
**Version:** v_0.0
**Resolves:** Geo-economic efficiency gap (generic macro theory → India-specific sector transmission)
**Companion edit:** Add Domain 44 row to 00_Index.md
