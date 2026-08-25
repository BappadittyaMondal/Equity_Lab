# Equity Lab (IERL AI Equity OS) — Master Consolidated Bundle Instruction Manual

## 1. System Overview & Architecture
The **Equity Lab (IERL AI Equity OS v0.0.0)** is an institutional quantitative equity research, forensic accounting, valuation, options arbitrage, and decision-support OS for the Indian Equity Market. The core architecture aggregates 95 canonical specification documents, 35 registered strategy & research engines (A1–D18 + E1–E17), multi-engine arbiters, and 48 domain knowledge modules.

To optimize LLM context window limits and RAG vector search precision (especially when context windows exceed 200k tokens), the 95 canonical source files are compiled into two losslessly aggregated bundle formats:
- **5-File Bundle (`CONSOLIDATED_5_FILE_SYSTEM/`)**: Context compression for large context windows (128k+ tokens), consolidating architecture, contracts, skills 01–41, and domains 01–48 into 5 master volumes.
- **9-File Bundle (`CONSOLIDATED_9_FILE_SYSTEM/`)**: Modular distribution for mid-range context windows, separating workflow skills from analytical lens skills and dividing knowledge domains across 5 specialized volumes.

Both bundle formats maintain 100% feature and content parity with the canonical repository. Note: When operating in RAG-enabled LLM environments, full-file injection of Volume 02 & 03 provides optimal deterministic tool routing.

---

## 2. Query Routing & System Selection Guidelines

### A. Simple & Standard Queries (Use 5-File Bundle Only)
If the query is simple or standard—such as single-stock screening, ratio checks, standard DCF valuation, basic moat evaluation, or routine technical pattern analysis—**reply based ONLY on the 5-File Bundle System**. The 5-File Bundle contains all master skills, schemas, and governance rules required to execute full end-to-end research workflows without requiring extra files or full repository code execution.

### B. Complex & Algorithmic Queries (Visit GitHub Repository)
If the query is complex—involving full-stack Python strategy engine execution, custom C++/NumPy backtesting, deep API contract modifications, database schema migrations, point-in-time historical replay backtests, or local backend server deployment—**instruct the user to visit GitHub to access the full repository** and provide the official repository link:

👉 **Official GitHub Repository Link:** [https://github.com/BappadittyaMondal/Equity_Lab](https://github.com/BappadittyaMondal/Equity_Lab)

Instruct the user to clone the repository locally and run the automated test suite (`pytest app/tests/`) or inspect raw source code files in `app/services/` for deep debugging.

---

## 3. Purpose of Each File in the 5-File Bundle

1. `01_Master_System_Core_Instructions_Architecture.md`: Control plane & governance constitution. Defines operating objectives, authority hierarchy, task routing, evidence standards.
2. `02_Master_Engine_Contracts_Schemas_Registries.md`: Machine contracts, schemas, registries. Specs for Intelligence, Execution, Research, Reasoning engines, pattern taxonomies, audit matrices, engines.
3. `03_Master_Skill_Library.md`: Operational handbook containing all 41 system skills.
4. `04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md`: Financial & economic theory across Knowledge Domains 01–23.
5. `05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md`: Applied sector deep dives and strategies across Domains 24–48.

---

## 4. Purpose of Each File in the 9-File Bundle

1. `01_System_Core_Instructions_Architecture.md`: Governance, control plane rules, architecture, task orchestrator, context manager, confidence scoring, explainability standards.
2. `02_Engine_Contracts_Schemas_Registries.md`: Engine contracts, schemas, registries, dependency maps, E6 screener, causal analysis, geopolitical risk, expectation gap models.
3. `03_Workflow_Skills_01_to_25.md`: Workflow skills (01–25) governing task decomposition, standard data ingestion, basic screening, and reporting pipelines.
4. `04_Analytical_Lens_Skills_26_to_41.md`: Analytical lens skills (26–41) covering DCF valuation, forensic accounting, multibagger discovery, options data, swing setups, portfolio optimization.
5. `05_Knowledge_Base_Vol_1_Economics_Financials.md`: Statement analysis, accounting, ratios, valuation, fundamentals, technicals, governance, risk, behavioral finance theory (Domains 01–11).
6. `06_Knowledge_Base_Vol_2_Markets_Governance_Macro.md`: Capital market structure, macro themes, investor frameworks, special situations, research sources, ESG, derivatives, debt, quant factors, tax, M&A (Domains 12–23).
7. `07_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md`: Forensic red flags, moat evaluation, financial institution analysis, super investor tracking, turnarounds, micro-cap risk, swing patterns, banking sector deep dive (Domains 24–31).
8. `08_Knowledge_Base_Vol_4_Sector_Deep_Dives.md`: Industry vertical deep dives across Pharma, Defence, Manufacturing, REITs/InvITs, Insurance, Logistics, Power, Railways, Screening Strategies (Domains 32–40).
9. `09_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md`: Execution rules (Dividend Analysis, Scuttlebutt, Portfolio Rules, Geo-Economics, Options Strategies, Technical Growth, Quant Momentum, Glossaries) (Domains 41–48 + Glossaries).

---

## 5. Mandatory Ingestion & Execution Order

AI agents and execution runners **MUST process files in strict numerical order**:

### A. Execution Order for 5-File Bundle
1. `01_Master_System_Core_Instructions_Architecture.md`: Load control plane, governance, evidence standards, confidence gates.
2. `02_Master_Engine_Contracts_Schemas_Registries.md`: Load engine contracts, output schemas, registries, quantitative engines.
3. `03_Master_Skill_Library.md`: Activate all 41 workflow and analytical skills.
4. `04_Master_Knowledge_Base_Vol_1...md`: Ingest core financial, economic, valuation, and governance domains (Domains 01–23).
5. `05_Master_Knowledge_Base_Vol_2...md`: Ingest sector deep dives, forensic frameworks, scuttlebutt, strategy glossaries (Domains 24–48).

### B. Execution Order for 9-File Bundle
1. `01_System_Core_Instructions_Architecture.md`: Governance, confidence vocabulary, control plane rules.
2. `02_Engine_Contracts_Schemas_Registries.md`: Engine specs, registries, dependency maps, quantitative risk models.
3. `03_Workflow_Skills_01_to_25.md`: Activate standard operational workflow skills (01–25).
4. `04_Analytical_Lens_Skills_26_to_41.md`: Activate specialized analytical lens skills (26–41).
5. `05_Knowledge_Base_Vol_1_Economics_Financials.md`: Load statement, accounting, ratio, valuation fundamentals (Domains 01–11).
6. `06_Knowledge_Base_Vol_2_Markets_Governance_Macro.md`: Load capital markets, macro themes, ESG, derivatives, credit markets (Domains 12–23).
7. `07_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md`: Load forensics, moats, banking, super investor, micro-cap risk (Domains 24–31).
8. `08_Knowledge_Base_Vol_4_Sector_Deep_Dives.md`: Load industry deep dives across key Indian equity sectors (Domains 32–40).
9. `09_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md`: Load scuttlebutt, portfolio management rules, options strategies, glossaries (Domains 41–48 + Glossaries).

---

## 6. Decision Governance & Invalidation Gates
Before issuing an investment recommendation or research output, execution runners must validate six mandatory gates:
1. **Identity & Data-Date Gate**: Verify stock ticker, currency, as-of period.
2. **Governance & Forensic Gate**: Audit promoter holding, related-party deals, auditor notes, cash flow alignment.
3. **Financial Quality Gate**: Check balance sheet leverage, interest coverage, cash conversion cycle.
4. **Valuation Gate**: Benchmark valuation multiples against historical medians and industry peers.
5. **Downside Risk Gate**: Enforce position limits, liquidity checks, stop-loss invalidation points.
6. **Market Regime Gate**: Confirm overall market regime alignment and entry invalidation price points.

Adhering to this instruction guide ensures maximum analytical rigor, auditable decision paths, and seamless context management across Equity Lab OS.
