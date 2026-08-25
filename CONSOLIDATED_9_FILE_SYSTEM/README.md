# Equity Lab — Consolidated 9-File System Specification

> **Granular Self-Sufficiency & LLM Context Readme**  
> This directory contains the modular 9-file architecture bundle of Equity Lab OS. Designed for context windows optimized for medium-sized modular chunks.

---

## 1. Bundle File Breakdown

1. `01_System_Core_Instructions_Architecture.md`: Core system architecture and orchestrators.
2. `02_Engine_Contracts_Schemas_Registries.md`: Engine specifications, object schemas, AST Custom Screener, Multibagger Engine.
3. `03_Workflow_Skills_01_to_25.md`: Core workflow execution skills.
4. `04_Analytical_Lens_Skills_26_to_41.md`: Advanced quantitative analytical lens skills.
5. `05_Knowledge_Base_Vol_1_Economics_Financials.md`: Financial statement analysis & microeconomics.
6. `06_Knowledge_Base_Vol_2_Markets_Governance_Macro.md`: Capital market structure & corporate governance.
7. `07_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md`: Forensic accounting, economic moats & banking frameworks.
8. `08_Knowledge_Base_Vol_4_Sector_Deep_Dives.md`: Sector-specific evaluation methodologies.
9. `09_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md`: Screening DSL, portfolio sizing, and financial glossaries.

---

## 2. LLM Context Ingestion Order

When feeding to an AI Agent or LLM, ingest in exact sequence: `01` through `09`.

---

## 3. Cryptographic Manifest Integrity

`MANIFEST.json` tracks the SHA-256 signatures of all 9 files.

### Verification Command
```bash
python -c "import json, hashlib; m=json.load(open('CONSOLIDATED_9_FILE_SYSTEM/MANIFEST.json')); [print(f, hashlib.sha256(open('CONSOLIDATED_9_FILE_SYSTEM/'+f, 'rb').read()).hexdigest() == v['sha256']) for f,v in m['bundle_files'].items()]"
```

---

## 4. Execution Command
```bash
pip install -r requirements.txt
python -m pytest app/tests/test_institutional_framework.py -q
uvicorn app.main:app --reload --port 8000
```
