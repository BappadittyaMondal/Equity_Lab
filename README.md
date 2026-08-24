# Equity Lab (v0.0.0)

> Institutional Indian Equity Research, Options Arbitrage, and Return Probability Engine

[![Repository](https://img.shields.io/badge/GitHub-BappadittyaMondal%2FEquity__Lab-blue)](https://github.com/BappadittyaMondal/Equity_Lab)
[![Python](https://img.shields.io/badge/Python-3.12%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#)

---

## 📌 Overview

**Equity Lab** is an institutional-grade quantitative stock screening, forensic accounting, valuation, and decision-support OS tailored for the Indian Equity Market. It integrates 35 deterministic strategy and research engines (18 Expert Strategy Modules A1–D18 + 17 Core Research Engines E1–E17) with a multi-engine Arbiter and Bull/Bear Debate framework.

---

## 🎯 Current Capability Scope

For a detailed breakdown of current system capabilities vs. future ML/RAG roadmap, see [Scope Decision v0.0](docs/SCOPE_DECISION_v0.0.md).

- **Current Version**: `v0.0.0`
- **Architecture**: Rule-based quantitative decision-support engine with point-in-time historical replay protection.
- **GitHub Repository**: [github.com/BappadittyaMondal/Equity_Lab](https://github.com/BappadittyaMondal/Equity_Lab)

---

## 🏃 Quick Start

```bash
# Clone the repository
git clone https://github.com/BappadittyaMondal/Equity_Lab.git
cd Equity_Lab

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run full test suite
pytest app/tests/ -v --basetemp=temp_pytest
```

---

## 🏛️ License & Provenance

Developed for institutional research and systematic screening. All strategy modules comply with strict point-in-time execution standards.
