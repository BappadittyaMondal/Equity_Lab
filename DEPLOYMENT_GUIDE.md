# DEPLOYMENT_GUIDE.md — Canonical Topology Manual

## 1️⃣ Target Deployment Topology

```
                       ┌─────────────────────────────────────────┐
                       │          Vercel Project (Frontend)      │
                       │                                         │
                       │  ┌───────────────────────────────────┐  │
                       │  │      frontend_deploy/ (Static)    │  │
                       │  │   index.html, style.css, js/*.js  │  │
                       │  └───────────────────────────────────┘  │
                       └──────────────────┬──────────────────────┘
                                          │
                                          │ API Requests (https://equity-lab-c90s.onrender.com)
                                          ▼
                       ┌─────────────────────────────────────────┐
                       │          Render Web Service (Backend)   │
                       │     FastAPI App (app/main.py:app)       │
                       └──────────────────┬──────────────────────┘
                                          │
                                          │ Database connection via DATABASE_URL
                                          ▼
                       ┌─────────────────────────────────────────┐
                       │            Render PostgreSQL            │
                       │       (Authoritative Data Store)        │
                       └─────────────────────────────────────────┘
```

- **Frontend Runtime**: Vercel Static (`@vercel/static`) building `frontend_deploy/`.
- **Backend Service**: Standalone Render Web Service running FastAPI (`https://equity-lab-c90s.onrender.com`).
- **Authoritative Database**: Render Hosted PostgreSQL (configured on Render backend via `DATABASE_URL`).
- **API Wrapper**: Frontend calls backend via `api.js` using Vercel environment variable `VITE_API_BASE` or `window.API_BASE` (with default fallback to `https://equity-lab-c90s.onrender.com`).
- **Deprecated Topologies**: Hostinger PHP hosting and Vercel `@vercel/python` serverless API handlers are DEPRECATED and out of scope.

---

## 2️⃣ Environment Variables Reference

### Render Backend Environment Variables (Render Dashboard)
```env
REQUIRE_AUTH=true
IERL_ENVIRONMENT=production
DATABASE_URL=postgres://username:password@ep-xyz.render.com/equity_lab_db?sslmode=require
API_KEY_SECRET=your_production_api_key_secret_here
ADMIN_API_KEY=your_production_admin_api_key_here
DATA_WRITE_API_KEY=your_production_write_api_key_here
ALLOWED_ORIGIN=https://your-frontend.vercel.app
OPENAI_API_KEY=your-openai-key
```

### Vercel Frontend Environment Variables (Vercel Dashboard)
```env
API_BASE=https://equity-lab-c90s.onrender.com
```

---

## 3️⃣ Vercel Routing Configuration (`vercel.json`)

```json
{
  "version": 2,
  "cleanUrls": true,
  "builds": [
    {
      "src": "frontend_deploy/**",
      "use": "@vercel/static"
    }
  ],
  "rewrites": [
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

## 4️⃣ Pre-flight & Build Gate

Before pushing changes to Git, execute:

```bash
python scripts/build_and_test.py
```

This verifies:
1. Integrity checks (`scripts/preflight_check.py`)
2. Full pytest suite (`app/tests/`)
