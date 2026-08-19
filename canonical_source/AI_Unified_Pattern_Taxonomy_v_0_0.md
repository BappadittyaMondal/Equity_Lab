<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Unified Pattern Taxonomy  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Unified_Pattern_Taxonomy_v_0.0

**Status:** Production Ready
**Category:** Cross-Cutting Standard (new — Rank 4, alongside Confidence Standard and Explainability Standard)
**Resolves:** Confirmed gap — technical, fundamental, macro, sector, market-cycle, operator, and sentiment domains each described "patterns" using different, non-shared vocabulary. This file makes them share one taxonomy.

---

## 1. Purpose

Seven domains in this project each independently describe "patterns" — Technical Analysis (chart patterns), Fundamental (Multibagger/Turnaround compounding chains, Domain 28), Macro (Domain 44 sector-transmission patterns), Sector (sector-cycle patterns), Market-Cycle (Domain 15 investor-framework cycles), Operator/Smart-Money (Domain 27 Super-Investor tracking, bulk/block deal patterns), and Sentiment (Retail Euphoria / Smart Money Exit from Risk Auditor). Before this file, each used its own ad hoc classification. This standard defines **7 universal pattern classes** that every domain maps onto — the domain-specific detection logic doesn't change, only the shared label each domain's finding gets tagged with.

---

## 2. The 7 Universal Pattern Classes

| Class | Definition | What It Looks Like Across Domains |
|---|---|---|
| **Continuation** | Existing trend/thesis is reinforced, not reversed | Technical: flag/pennant. Fundamental: earnings beat confirming an existing growth thesis. Macro: a rate-cut cycle continuing as expected. Operator: an ace investor adding to an existing position. |
| **Reversal** | Direction changes from what preceded it | Technical: head-and-shoulders. Fundamental: a turnaround company (Domain 28) posting its first profitable quarter after losses. Macro: a rate cycle inflection. Sentiment: Smart Money Exit turning to Smart Money Entry. |
| **Distribution** | Smart money/quality participants reducing exposure while it isn't yet visible in price | Technical: high volume on declines, low volume on rallies. Operator: ace investor bulk-deal selling (Domain 27). Sentiment: Retail Euphoria rising while institutional holding falls (Risk Auditor Flag 1). |
| **Accumulation** | Smart money/quality participants building exposure before it's visible in price | Technical: high volume on advances within an apparent range. Operator: ace investor bulk-deal buying. Fundamental: promoter holding increasing while price is flat (Domain 8 governance signal). |
| **Volatility** | A compression or expansion phase that precedes a directional move, not itself directional | Technical: Bollinger Band squeeze. Macro: pre-election or pre-budget uncertainty compression (Domain 44 macro layer). Sector: pre-regulatory-announcement uncertainty in a sector (e.g., pending PLI disbursement decision). |
| **Failed Pattern** | A pattern that triggered but then reversed — treated as a signal in the OPPOSITE direction, not "no signal" | Technical: a false breakout (Technical Analysis Skill's Failed Pattern rule). Fundamental: a Multibagger candidate that passed the Quick Screen but then failed a subsequent quarter's numbers — treat as a downgrade signal, not neutral. Macro: an expected rate cut that doesn't materialize — treat as hawkish, not neutral. |
| **Confirmation State** | Not a pattern itself, but the required condition before any pattern above is actionable | Technical: Volume Confirmation (≥1.5x average). Fundamental: 2+ source corroboration (Research Engine Multi-Source Validation). Operator: bulk deal confirmed via exchange filing, not rumor. |

---

## 3. Domain Mapping Table

| Domain/Skill | Existing Pattern Vocabulary | Maps To Universal Class |
|---|---|---|
| Technical Analysis Master Skill (Module 6) | Chart patterns (H&S, flags, triangles) | Continuation / Reversal, per pattern type |
| Technical Analysis (Pattern Taxonomy Extension) | Distribution/Accumulation/Volatility/Failed | **Already uses these exact class names** — this file generalizes them project-wide |
| Domain 28 (Multibagger & Turnaround Framework) | Compounding chain, Category A/B | Continuation (compounding chain) / Reversal (turnaround) |
| Domain 27 (Super-Investor Tracking) | Bulk/block deal signals | Accumulation / Distribution, depending on direction |
| Domain 44 (Geo-Economic Impact) | Sector transmission mechanisms | Continuation (expected transmission) / Reversal (surprise policy shift) / Volatility (pre-decision uncertainty) |
| Risk Auditor (Smart Money Exit, Retail Euphoria) | Ownership-flow risk flags | Distribution (Smart Money Exit) / the inverse is Accumulation |
| Domain 15 (Investor Frameworks) | Market cycle stages | Continuation / Reversal at the macro-cycle level |
| Sector Quick-Reference | Sector-specific red flags | Mostly Reversal (a sector red flag typically signals a coming reversal) or Volatility (regulatory uncertainty) |

---

## 4. Cross-Domain Reinforcement Rule

**Why this matters more than a naming convention:** once every domain tags findings with the same 7 classes, a genuinely new capability becomes possible — checking whether *multiple domains* are independently flagging the *same class* for the same company/sector, which is a much stronger signal than any single domain's finding alone.

```
IF Technical Analysis flags "Distribution" (high volume on declines)
   AND Operator/Domain 27 flags "Distribution" (ace investor bulk-deal selling)
   AND Risk Auditor flags "Distribution" (Smart Money Exit — FII/DII both declining)
THEN this is Cross-Domain-Confirmed Distribution — materially higher
     confidence than any single domain's signal alone (per Confidence
     Standard §12, this should use the highest applicable Source Tier
     weighting, not be averaged down by treating each domain as an
     independent, equally-weighted vote)

IF domains disagree (e.g., Technical shows Accumulation, but Operator
   shows Distribution) THEN state the conflict explicitly — this is
   exactly the kind of disagreement Reasoning Skills' Contradiction
   Detection Method (Part 1 Addition 2) is designed to catch, now
   with a shared vocabulary making the conflict easy to spot at all.
```

---

## 5. Required Cross-References

This standard is now Rank 4 alongside `AI_Confidence_Standard` and `AI_Explainability_Standard`. Add one line to each domain/skill file that already had its own pattern vocabulary:

```
Pattern classifications in this file map to the 7 universal classes
defined in AI_Unified_Pattern_Taxonomy_v1.0.md.
```

This is a single-line addition per file — no restructuring of any existing domain's own detection logic.

---

## 6. Self-Audit

- ✓ Does not replace any domain's existing detection method — Technical Analysis still uses its own indicator logic, Domain 27 still uses its own bulk-deal criteria
- ✓ Adds a shared label layer only, enabling the new Cross-Domain Reinforcement Rule (Section 4) — this is the genuine new capability, not just tidier naming
- ✓ Consistent with existing Confidence Standard weighting — cross-domain confirmation is not a new math model, it reuses the existing Source Tier weighting logic

---

# Document Information

**Document:** AI_Unified_Pattern_Taxonomy_v_0.0.md
**Version:** v_0.0
**Resolves:** Confirmed gap — no unified pattern taxonomy existed across technical/fundamental/macro/sector/market-cycle/operator/sentiment domains
**New Rank:** 4 (Cross-Cutting Standard)
