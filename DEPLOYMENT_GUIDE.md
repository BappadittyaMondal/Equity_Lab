# DEPLOYMENT_GUIDE.md

## Overview
This guide provides a step‑by‑step, zero‑knowledge process for deploying the **IERL Equity Intelligence OS** on **Hostinger Business plan** (static hosting + Python app). Follow it on a fresh clone to achieve a fully functional production deployment.

---

## 1️⃣ Prerequisites
- **Git** (clone the repository)
- **Hostinger account** with a *Python App* enabled (Business plan)
- **Python version**: `3.11` (matching the `.python-version` file at the repository root)
- **Environment variables** – see section 2 below. **Never commit** a `.env` file to the repository.

---

## 2️⃣ Environment Variables
Create a file named `API_KEYS_CONFIG.env` **outside** the repository (e.g. in your home directory) and populate it with the following keys. Then copy the values into Hostinger’s *Environment Variables* UI (Settings → Environment Variables).
```
IERL_ENVIRONMENT=production
CACHE_TTL_QUOTE_SEC=30            # seconds before a quote is considered stale
CACHE_TTL_FUNDAMENTALS_SEC=300    # seconds before fundamentals are stale
PRICE_CONFLICT_TOLERANCE_PCT=5    # tolerance for price‑conflict handling
SKILL_LIBRARY_VERSION=5
REQUIRE_AUTH=true
# LLM / data provider keys – replace with your own values
OPENAI_API_KEY=your-openai-key
ALPHAVANTAGE_API_KEY=your-av-key
# ... any other keys required by services/*.py
```
> **Security note** – do **not** commit `API_KEYS_CONFIG.env`. Add it to `.gitignore` (see section 9).

---

## 3️⃣ Procfile (already present)
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Hostinger will automatically use this entry point when you enable *Python App*.

---

## 4️⃣ Repository Structure (relevant parts)
```
.
├─ app/                 # FastAPI backend
│   ├─ api/            # API routers (decision, watchlist, health …)
│   ├─ core/           # config, constants
│   └─ services/       # business logic
├─ frontend_deploy/    # static HTML/JS/CSS (zero‑build)
├─ scripts/            # nightly cron scripts
├─ data/                # SQLite DB (must stay outside static root)
├─ .python-version      # pins Python 3.11
├─ Procfile
├─ DEPLOYMENT_GUIDE.md  # THIS FILE
└─ ...
```
The **static root** for Hostinger is `frontend_deploy/`. Anything under `data/` is **not** publicly served.

---

## 5️⃣ Pre‑flight Check (manual step)
Before pushing any change, run the test suite locally to catch regressions:
```bash
python scripts/preflight_check.py
```
The script runs the core unit tests (market‑data cache, conviction API, etc.) and exits with a non‑zero status on failure, preventing accidental deployment of broken code.

---

## 6️⃣ Nightly Cron Job (watchlist scan)
The system requires a nightly scan that refreshes the watchlist and updates conviction scores.
### 6.1 Add the cron entry in Hostinger
In the Hostinger **Cron Jobs** UI add the following line (adjust the username and repo path accordingly):
```
0 2 * * * /home/username/your_repo/scripts/nightly_watchlist_scan.py >> /home/username/cron.log 2>&1
```
- **Schedule**: 02:00 AM server time (adjust if you prefer a different slot).
- **Working directory**: the command runs relative to the cloned repository, so ensure the path points to the repo root.
- The script writes a log line `Nightly watchlist scan completed` on success.

### 6.2 Verify the cron
After a day, inspect the log:
```bash
cat /home/username/cron.log | grep "Nightly watchlist scan completed"
```
You should see a timestamped entry confirming the run.

---

## 7️⃣ SQLite Database Location & Permissions
- The SQLite file lives at `data/ierl_equity.sqlite3` (outside `frontend_deploy`).
- Hostinger’s shared filesystem runs the app under the user `your_user`. Run the following once after the first deployment:
```bash
chmod 664 data/ierl_equity.sqlite3
chown $USER:www-data data/ierl_equity.sqlite3   # replace $USER with your Hostinger user
```
This ensures the FastAPI process can read/write the DB.

---

## 8️⃣ Health‑check Verification
After deployment, confirm the app is alive:
```bash
curl https://<your‑app>.hostingerapp.com/api/v1/health
```
Expected JSON response:
```json
{"status":"ok"}
```
If you receive a 5xx error, check the Hostinger logs (App → *Logs*) for stack traces.

---

## 9️⃣ .gitignore – keep secrets out of VCS
Add the following lines to `.gitignore` (or ensure they exist):
```
# Environment secrets
API_KEYS_CONFIG.env
.env

# Runtime data files
/data/ierl_equity.sqlite3
```
Commit the updated `.gitignore`.

---

## 🔟 Final Checklist (run once after a fresh clone)
1. Clone the repo.
2. Create `API_KEYS_CONFIG.env` locally (outside the repo) and copy the values to Hostinger.
3. Verify `.python-version` matches Hostinger’s Python version (3.11).
4. Run `python scripts/preflight_check.py` – all tests must pass.
5. Deploy via Hostinger’s *Git Integration* or manual push.
6. Check `/api/v1/health` returns `200`.
7. Add the **cron** entry for the nightly scan.
8. Verify the cron log after 24 h.
9. Browse the UI – conviction‑call and watchlist panels should load without inline scripts.

---

## 11️⃣ Load Baseline & VPS Upgrade Triggers
- **Benchmark Baseline (Hostinger Shared Hosting simulation)**:
  - 10 Concurrent Workers x 20 Requests (200 Total).
  - Throughput Capacity: ~57 requests/sec.
  - Average Latency: 171 ms (P95: 580 ms).
  - Zero 5xx server crashes (100% system stability under rate-limiting protection).
- **VPS Upgrade Trigger Conditions**:
  - Upgrade from Hostinger Shared Business Hosting to a Dedicated KVM VPS (2 vCPU / 4GB RAM) if:
    1. Active user concurrency exceeds 15 simultaneous real-time analytical sessions.
    2. Nightly cron watchlist scanning takes > 30 minutes for > 500 equities.
    3. SQLite WAL lock contention causes P95 latencies to exceed 1500 ms.

---

*By following this guide, any developer can reproduce a production‑ready deployment without tribal knowledge.*
