# DEPLOYMENT_GUIDE.md

## Overview
This guide provides an end-to-end, zero-knowledge operational manual for deploying the **Equity Lab OS** on **Vercel** (Frontend + FastAPI Serverless API) paired with **Render PostgreSQL** as the authoritative production database.

---

## 1️⃣ Target Deployment Topology

```
                       ┌─────────────────────────────────────────┐
                       │          Vercel Single Project          │
                       │                                         │
                       │  ┌───────────────────────────────────┐  │
                       │  │      frontend_deploy/ (Static)    │  │
                       │  │   index.html, style.css, js/*.js  │  │
                       │  └───────────────────────────────────┘  │
                       │                   │                     │
                       │        API requests (/api/v1/*)         │
                       │                   ▼                     │
                       │  ┌───────────────────────────────────┐  │
                       │  │   api/index.py (FastAPI Server)   │  │
                       │  │   Serverless Function (@vercel/py)│  │
                       │  └───────────────────────────────────┘  │
                       └──────────────────┬──────────────────────┘
                                          │
                                          │ Database connection via DATABASE_URL
                                          ▼
                       ┌─────────────────────────────────────────┐
                       │            Render PostgreSQL            │
                       │       (Authoritative Data Store)        │
                       └─────────────────────────────────────────┘
```

- **Runtime**: `@vercel/python` (Python 3.11 / 3.12).
- **API Entrypoint**: `api/index.py` (exposes `app` from `app.main`).
- **Static Root**: `frontend_deploy/`.
- **Authoritative Database**: Render Hosted PostgreSQL (configured via `DATABASE_URL`).
- **Local Fallback**: Ephemeral SQLite (`/tmp/ierl_research.db`) during cold-starts when `DATABASE_URL` is omitted.

---

## 2️⃣ Environment Variables Reference

Configure the following environment variables in the **Vercel Dashboard** (*Settings → Environment Variables*):

```env
# General
VERCEL=1
REQUIRE_AUTH=true
IERL_ENVIRONMENT=production

# Database (Render PostgreSQL)
DATABASE_URL=postgres://username:password@ep-xyz.render.com/equity_lab_db?sslmode=require

# API Keys & Secrets
API_KEY_SECRET=your_production_api_key_secret_here
ADMIN_API_KEY=your_production_admin_api_key_here
DATA_WRITE_API_KEY=your_production_write_api_key_here

# CORS Configuration
ALLOWED_ORIGIN=https://your-app-name.vercel.app

# Optional Data Provider Keys
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
ALPHAVANTAGE_API_KEY=your-av-key
```

> **Security Note**: NEVER commit `.env` or `API_KEYS_CONFIG.env` files to Git. All environment variables must be managed exclusively in Vercel and Render dashboards.

---

## 3️⃣ Vercel Routing Configuration (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend_deploy/**",
      "use": "@vercel/static"
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/",
      "destination": "/frontend_deploy/index.html"
    },
    {
      "source": "/(.*)",
      "destination": "/frontend_deploy/$1"
    }
  ]
}
```

---

## 4️⃣ Render PostgreSQL Database Setup

1. Log into [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **PostgreSQL**.
3. Name the database `equity-lab-db`, choose region closest to your Vercel deployment (e.g. `us-east-1` or `singapore`), and select the plan.
4. Copy the **External Connection String** (`postgres://...`).
5. Add `DATABASE_URL` to Vercel Environment Variables.
6. (Optional) Run the migration script locally to populate seed records into PostgreSQL:
   ```bash
   DATABASE_URL="postgres://user:pass@render-host/db" python scripts/migrate_sqlite_to_postgres.py
   ```

---

## 5️⃣ Clean-Room Pre-flight & Build Gate

Before pushing any changes to Git or Vercel, run the canonical clean-room build verification script:

```bash
.venv\Scripts\python scripts/build_and_test.py
```

This single command executes:
1. Automated Preflight Integrity Checks (`scripts/preflight_check.py`)
2. Full pytest suite (`app/tests/`) — 411/411 tests must pass.

---

## 6️⃣ Deployment Steps

### Option A: GitHub + Vercel Integration (Recommended)
1. Commit and push your changes to GitHub:
   ```bash
   git add .
   git commit -m "feat: release production build"
   git push origin main
   ```
2. Import the repository in [Vercel Dashboard](https://vercel.com/new).
3. Set Framework Preset to **Other**.
4. Configure Environment Variables (Section 2).
5. Click **Deploy**.

---

## 7️⃣ Health & System Verification

After deployment succeeds, run the following verification commands:

```bash
# 1. Health check probe
curl https://your-app.vercel.app/api/v1/health

# 2. Database & system readiness probe
curl https://your-app.vercel.app/api/v1/readiness
```

Expected JSON response from `/api/v1/health`:
```json
{
  "status": "ONLINE",
  "system": "IERL Equity Intelligence OS",
  "version": "0.4.0",
  "providers_status": {
    "yfinance_nse": "ONLINE"
  }
}
```
