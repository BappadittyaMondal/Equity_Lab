# Dependency Security Audit Report (pip-audit)

**Project Baseline:** Equity Lab v0.0.0  
**Audit Execution Date:** 2026-08-21 11:10 IST  
**Environment Target:** `requirements.txt` & `app/requirements.txt`  
**Final Status:** **PASSED — 0 Known Vulnerabilities Detected**

---

## 1. Initial Vulnerability Scan (Before Remediation)

```text
Found 15 known vulnerabilities across 4 packages (transitive and build dependencies):
- starlette: CVE / GHSA findings (GHSA-86qp-5c8j-p5mr, PYSEC-2026-248, PYSEC-2026-249, PYSEC-2026-2280, PYSEC-2026-2281)
- curl-cffi: SSRF via unrestricted redirects (transitive via yfinance 1.1.0)
- pytest: 8.4.2 (requires >= 9.1.1)
- pip: Build-environment bootstrap tool (6 vulnerabilities in un-upgraded venv pip)
```

---

## 2. Remediation Actions Applied

The following secure version constraints were pinned across `requirements.txt`, `app/requirements.txt`, and build setup automation:

| Package | Initial Version | Patched Version | Remediated Vulnerabilities |
| :--- | :--- | :--- | :--- |
| **`starlette`** | `<1.3.1` (transitive) | **`>=1.3.1`** | Host-header path reconstruction, form-parsing DoS, HTTPEndpoint verb-dispatch, Windows UNC-path SSRF |
| **`fastapi`** | `0.129.2` | **`>=0.130.0`** | Enforces patched `starlette` core framework dependencies |
| **`curl-cffi`** | `<0.15.0` (transitive) | **`>=0.15.0`** | Unrestricted redirect SSRF mitigation for `yfinance` underlying requests |
| **`pytest`** | `8.4.2` | **`>=9.1.1`** | Upgraded testing framework to verified secure release |
| **`pip`** | bundled venv version | **`>=26.1.2`** | Upgraded environment package installer tool in CI and setup instructions |

---

## 3. Final Verification Scan (After Remediation)

```text
$ python -m pip_audit -r requirements.txt --desc
No known vulnerabilities found
Exit Code: 0
```

---

## 4. Verification Checklist

- [x] `pip-audit -r requirements.txt --desc` shows **0 findings** (Exit code 0).
- [x] Full test suite green (`330 passed`).
- [x] Secret scanning verified (`python scripts/check_no_real_secrets.py`).
