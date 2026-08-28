# Equity Lab — Consolidated 5-File System Specification

> **Self-Sufficiency & LLM Context Readme**  
> This directory contains the complete, self-contained 5-file architecture bundle of Equity Lab OS. An external AI agent or developer can fully understand, build, and deploy the entire system using ONLY these 5 files.

---

## 1. Bundle File Breakdown

1. `01_Master_System_Core_Instructions_Architecture.md`: System Core, Orchestration, Context Rules, Confidence & Explainability Standards.
2. `02_Master_Engine_Contracts_Schemas_Registries.md`: All Strategy Engines, Machine Contracts, JSON Schemas, AST Screener & Multibagger Specifications.
3. `03_Master_Skill_Library.md`: Complete Workflow and Analytical Lens Skill Tree (Skills 01–41).
4. `04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md`: Microeconomics, Financial Analysis, DCF Valuation, Forensics & Governance.
5. `05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md`: Macroeconomics, Banking/NBFC Forensics, Sector Deep Dives, Screening & Portfolio Construction.

---

## 2. LLM Context Ingestion Order

When feeding this project to an AI Agent or LLM with limited context window, ingest the files in exact numerical order:

```text
[1] 01_Master_System_Core_Instructions_Architecture.md
[2] 02_Master_Engine_Contracts_Schemas_Registries.md
[3] 03_Master_Skill_Library.md
[4] 04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md
[5] 05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md
```

---

## 3. Cryptographic Manifest & Integrity Rules

The file `MANIFEST.json` in this directory contains SHA-256 hashes of all 5 bundle files, source-mapping metadata, git commit hash, and generator timestamp.

### Verification Command
To verify bundle integrity:
```bash
python -c "import json, os; m=json.load(open('CONSOLIDATED_5_FILE_SYSTEM/MANIFEST.json')); [print(f['filename'], os.path.getsize('CONSOLIDATED_5_FILE_SYSTEM/'+f['filename']) == f['bytes']) for f in m['files']]"
```

---

## 4. Fresh Environment Execution

To run Equity Lab OS from a fresh environment using this repository:
```bash
pip install -r requirements.txt
python -m pytest app/tests/test_institutional_framework.py -q
uvicorn app.main:app --reload --port 8000
```
