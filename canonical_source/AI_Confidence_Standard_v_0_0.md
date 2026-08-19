<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Confidence Standard  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_Confidence_Standard_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Cross-Cutting Standard
**Priority:** Critical
**Role:** Universal Confidence Framework
**Encoding:** UTF-8 (corrects v_0.0 UTF-16LE defect -- CV-04)
**Architectural Authority:** AI_System_Constitution prevails over this standard on any conflict.
**Scope Clarification:** This standard defines confidence *representation*, not truth or probability of an outcome. Confidence measures the reliability of process and evidence -- never the likelihood that a prediction will be correct.

---

# Table of Contents

## Part 1 -- Confidence Architecture
1. Purpose, 2. Vision, 3. Scope, 4. Design Philosophy, 5. Responsibilities, 6. Non-Responsibilities, 7. Universal Principles, 8. Confidence Lifecycle

## Part 2 -- Confidence Model
9. Confidence Levels & Numeric Mapping, 10. Confidence Sources, 11. Confidence Categories, 12. Confidence Aggregation Formula, 13. Confidence Propagation & Calibration, 14. Confidence Metadata, 15. Confidence Validation

## Part 3 -- Engine Confidence Standards
16-22. Task / Research / Evidence / Reasoning / Decision / Audit / Output Confidence

## Part 4 -- Governance
23. Universal Rules, 24. Compliance, 25. Future Extensions, 26. Final Specification

---

# PART 1 -- CONFIDENCE ARCHITECTURE

# 1. Purpose
Defines how confidence is represented, calculated, propagated, and reported across the AI Operating System. All engines use this common framework -- no engine defines its own confidence vocabulary or math.

# 2. Vision
A transparent, mathematically reproducible measure of certainty at every pipeline stage. Confidence reflects the reliability of available information and processing quality -- not correctness of the eventual outcome.

# 3. Scope
Applies to: Task Orchestrator, Intelligence Engine, Research Engine, Reasoning Skills, Quality Audit, Output System.

# 4. Design Philosophy
Confidence shall be: Consistent, Explainable, Evidence-based, Traceable, Comparable, Versioned, and Numerically reproducible (new in v_0.0).

# 5. Responsibilities
This standard defines: confidence representation, numeric scoring, aggregation formula, propagation rules, calibration behavior, metadata, validation.

# 6. Non-Responsibilities
Does not: perform reasoning, make decisions, override evidence, replace Quality Audit, predict outcomes.

# 7. Universal Principles
Confidence shall never exceed evidence quality; shall decrease when uncertainty increases; shall be explainable, traceable, and -- as of v_0.0 -- reproducible from a stated formula, not a subjective judgment.

# 8. Confidence Lifecycle
```
Generated -> Validated -> Propagated -> Consumed -> Archived
```

---

# PART 2 -- CONFIDENCE MODEL

# 9. Confidence Levels & Numeric Mapping

This is the primary gap closed from v_0.0 (Forensic Audit MV-01: no quantitative model existed).

| Level | Score Range | Interpretation |
|---|---|---|
| Very High | 0.85 - 1.00 | Strong, multi-source, internally consistent evidence; no material contradictions |
| High | 0.70 - 0.84 | Solid evidence base; minor gaps or single-source reliance on non-critical points |
| Moderate | 0.50 - 0.69 | Adequate evidence with identifiable gaps or some unresolved conflict |
| Low | 0.30 - 0.49 | Weak or thin evidence; significant gaps or unresolved conflicts |
| Very Low | 0.00 - 0.29 | Minimal or contradictory evidence; conclusion is provisional at best |

ConfidenceScore is always a float in [0.00, 1.00]. ConfidenceLevel is the label derived by table lookup -- never assigned independently of the score.

# 10. Confidence Sources
Evidence Quality, Source Reliability, Data Completeness, Research Coverage, Logical Consistency, Validation Results.

Source Reliability Weight Table (used in Section 12):

| Source Tier | Weight |
|---|---|
| Primary (exchange filings, audited financials, regulatory filings) | 1.00 |
| Secondary (reputable financial media, sell-side research) | 0.70 |
| Tertiary (aggregator sites, unverified commentary) | 0.40 |

# 11. Confidence Categories
Task, Research, Evidence, Reasoning, Decision, Audit, Output Confidence -- each computed per Part 3.

# 12. Confidence Aggregation Formula

Evidence to Research Confidence (weighted mean by source credibility):

```
ResearchConfidence = Sum(weight_i x confidence_i) / Sum(weight_i)

where:
  confidence_i = individual EvidenceObject's ConfidenceScore
  weight_i     = Source Reliability Weight (Section 10 table)
```

Coverage Penalty: If Research Engine's completeness gate (Research Engine section 22) reports coverage below its threshold, apply a multiplicative penalty:

```
AdjustedResearchConfidence = ResearchConfidence x CoverageFactor

where CoverageFactor = min(1.0, ActualCoverage / RequiredCoverage)
```

Reasoning to Decision Confidence:

```
DecisionConfidence = AdjustedResearchConfidence x ConsistencyFactor

where ConsistencyFactor in [0.6, 1.0]:
  1.0  -> no unresolved contradictions in evidence
  0.8  -> minor contradictions, disclosed and reconciled
  0.6  -> material contradiction presented as competing scenarios
         (per Reasoning Skills conflict handling -- never suppressed)
```

Audit Confidence: equals DecisionConfidence unless Quality Audit's own review identifies a defect not visible upstream (e.g., a bias flag), in which case Quality Audit may apply a further documented reduction -- never an increase (per Section 13).

Output Confidence: equals the final AuditConfidence passed through unchanged. The Output System never recalculates confidence -- it only renders it (per AI_Output_System_v_0.0.md section 14).

# 13. Confidence Propagation & Calibration

Core Rule (unchanged from v_0.0, now formalized):

```
OutputConfidence <= AuditConfidence <= DecisionConfidence
                  <= AdjustedResearchConfidence <= max(EvidenceConfidence_i)
```

Confidence is monotonically non-increasing as it moves downstream, with exactly one exception:

Calibration Exception: A downstream stage may increase confidence only when it obtains genuinely new supporting evidence not available upstream (e.g., Quality Audit cross-validates a claim against an independent source the Research Engine didn't have access to). Any such increase must be logged in ConfidenceInheritedFrom with an explicit CalibrationReason field -- silent increases are a standard violation (Section 23).

# 14. Confidence Metadata

Every confidence value includes:

```yaml
ConfidenceLevel:            # table lookup from Section 9
ConfidenceScore:             # float 0.00-1.00
AssessmentBasis:              # which formula/rule produced this value
ConfidenceSource:             # engine that generated it
ConfidenceInheritedFrom:      # upstream ConfidenceScore(s) consumed
SupportingFactors: []
LimitingFactors: []
CalibrationReason:            # only present if Section 13 exception applied
Timestamp:
```

# 15. Confidence Validation
Every confidence assessment shall be: evidence-backed, internally consistent with the aggregation formula (Section 12), explainable, traceable, and reproducible -- i.e., re-running the formula on the same inputs yields the same score.

--

# 15A. Confidence Decay Horizons (Addition)

Evidence confidence decays over time. Apply a StalenessFlag when
evidence age exceeds its category horizon:

| Category | Staleness Horizon |
|---|---|
| Financial statement data | 90 days |
| Regulatory/compliance status | 30 days |
| Governance/promoter assessment | 180 days |
| Technical/price data | 7 days |
| Shareholding pattern | 90 days (one quarter) |

StalenessFlag: true -> the evidence is treated as a starting point
requiring re-verification, not a current fact. Apply a confidence
penalty consistent with Section 12's CoverageFactor mechanism:
EvidenceConfidence is multiplied by 0.85 when StalenessFlag is true
and no fresher corroborating evidence exists.

---

# 15B. Canonical Data & Evidence Quality Chain

To guarantee that weak sources directly lower downstream decisions, every task execution enforces a single, traceable quality chain:

`Source → Evidence → Quality → Confidence → Decision → Output`

### 1. Evidence Quality Metrics
Every `EvidenceObject` must capture the following metadata parameters:
*   **SourceTier**: `Primary` (weight = 1.0), `Secondary` (weight = 0.7), or `Tertiary` (weight = 0.4).
*   **RetrievalTimestamp**: The ISO-8601 timestamp when the data was scraped or ingested.
*   **AsOfDate**: The original reporting date of the underlying source record.
*   **Freshness**: Calculated dynamically: `Freshness = (CurrentTime - AsOfDate) <= StalenessHorizon`.
*   **Completeness**: A ratio `[0.0, 1.0]` of expected fields successfully extracted.
*   **ContradictionFlag**: Set to `true` if this evidence conflicts with another loaded evidence item.
*   **Provenance**: A verifiable URI/link pointing to the exact page, table, or line of the source.
*   **PrimarySourceAvailability**: `true` if a primary document was audited; `false` if secondary reports were used.
*   **DataQualityStatus**: One of `VERIFIED` | `UNVERIFIED` | `STALE` | `CORRUPTED`.

### 2. Math for Downstream Impact
A weak source lowers downstream confidence according to the following formulas:

```
AdjustedEvidenceConfidence = SourceTierWeight * Completeness * StalenessPenalty * VerificationPenalty

Where:
  StalenessPenalty = 0.85 if (Freshness == False) else 1.0
  VerificationPenalty = 0.70 if (DataQualityStatus == UNVERIFIED) else 1.0
```

If any critical piece of evidence (e.g., forensic risk or accounting data) has an `AdjustedEvidenceConfidence < 0.50`, it limits the overall `DecisionConfidence` to a maximum ceiling of `0.50` (Moderate), regardless of other high-quality inputs.

---


# PART 3 -- ENGINE CONFIDENCE STANDARDS

# 16. Task Confidence
Measures: interpretation certainty of user intent. Inputs: ambiguity signals from Task Orchestrator's classification step. Output: informs whether ClarificationRequest is triggered. Upstream relationship: none -- first confidence generated.

# 17. Research Confidence
Measures: completeness and reliability of collected research. Inputs: weighted evidence scores (Section 12) + coverage factor. Output: AdjustedResearchConfidence. Upstream relationship: aggregates all EvidenceConfidence values.

# 18. Evidence Confidence
Measures: quality/reliability of one evidence item. Inputs: source tier weight (Section 10) + Research Engine's own source validation. Output: per-item ConfidenceScore. Upstream relationship: none -- atomic input.

# 19. Reasoning Confidence
Measures: logical strength and internal consistency of reasoning. Inputs: AdjustedResearchConfidence + ConsistencyFactor. Output: feeds Decision Confidence. Upstream relationship: derived from Research Confidence.

# 20. Decision Confidence
Measures: confidence in the DecisionObject's conclusion. Inputs: Section 12 formula. Output: DecisionConfidence. Upstream relationship: = Research Confidence x Consistency Factor.

# 21. Audit Confidence
Measures: confidence after independent validation. Inputs: DecisionConfidence, adjusted only downward unless Section 13 exception applies. Output: AuditConfidence. Upstream relationship: <= Decision Confidence.

# 22. Output Confidence
Measures: final confidence shown to the user. Inputs: AuditConfidence, passed through unchanged. Output: rendered per AI_Output_System_v_0.0.md section 14/15. Upstream relationship: = Audit Confidence exactly.

---

# PART 4 -- GOVERNANCE

# 23. Universal Rules
Always: separate confidence from certainty; base confidence on the Section 12 formula; explain confidence via metadata; preserve confidence history; maintain traceability.
Never: inflate confidence; hide uncertainty; ignore contradictory evidence; increase confidence downstream without a logged Calibration Reason.

# 24. Compliance
Every engine implements this standard's formula exactly -- not an approximation. Non-compliant confidence calculations are architectural defects.

# 25. Future Extensions
Additional confidence categories may be added without changing the core aggregation formula, provided they follow the monotonic propagation rule.

# 26. Final Specification
The AI Confidence Standard v_0.0 defines a mathematically reproducible method for representing and propagating confidence across the AI Operating System. It resolves CV-04 (UTF-16 encoding made v_0.0 unreadable -- this document is plain UTF-8) and MV-01 (no aggregation formula existed -- Section 12 now provides one).

---

# Document Information

Document: AI_Confidence_Standard_v_0.0.md
Version: v_0.0
Supersedes: AI_Confidence_Standard_v_0.0 (UTF-16 encoded, no numeric model)
Status: Production Ready
Applies To: All Core Engines, All Future Engines
Resolves: CV-04, MV-01
Architecture State: Frozen

# END OF DOCUMENT

