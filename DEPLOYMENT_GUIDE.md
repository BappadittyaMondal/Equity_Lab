# IERL AI Equity OS — Production Deployment & Operational Runbook

## 1. System Requirements & Stack
- **Backend**: Python 3.10+ with FastAPI, uvicorn, yfinance, pandas, numpy, pydantic v2.
- **Frontend**: HTML5 / Standalone Production CSS (`style.css`) served via FastAPI or CDN/Hostinger static hosting.
- **Deployment Platform**: Render.com / Hostinger / AWS EC2 / Docker.

## 2. Environment Variables Reference
For local development only, copy `.env.example` to `.env`. Hosted deployments must use the platform's environment-variable/secret-store facility; do not upload `API_KEYS_CONFIG.env`. The legacy key file is not loaded unless `IERL_LOAD_LEGACY_API_KEYS_FILE=true` is deliberately set during local migration.

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `ACTIVE_LLM_PROVIDER` | No | `gemini` | Reserved provider selector; the current runtime implements Gemini only |
| `GEMINI_API_KEY` | Optional | `""` | Google Gemini 1.5 Flash API Key |
| `GROQ_API_KEY` | Optional | `""` | Groq Llama-3 API Key |
| `ALLOWED_ORIGIN` | Yes | `https://sovereignmind.in` | Permitted CORS origins (comma separated) |
| `REQUIRE_AUTH` | No | `false` | Require `X-API-Key` on non-health API requests |
| `API_KEY_SECRET` | Required when auth is enabled | `""` | API key stored only in the hosting platform's secret manager |
| `IERL_ENVIRONMENT` | Yes | `production` | Prevents local dotenv files from being loaded in hosted deployments |
| `ENABLE_OPTIONS_A2` | No | `false` | Must remain false until the options model is validated |

## 3. Running the Server Locally
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open `http://127.0.0.1:8000/` in browser.

## 4. Running Backend Tests
```bash
python -m pytest app/tests
```

## 5. Docker Deployment
```bash
docker build -f app/Dockerfile -t ierl-equity-os .
docker run -p 8000:8000 --env-file .env ierl-equity-os
```

## 6. Operational Runbook
- **Provider Outage (yfinance / NSE)**: Backend returns structured HTTP 503 Service Unavailable errors. Frontend automatically renders explicit "Data Stream Degraded" UI state without concealing failure.
- **API Key Rotation**: Rotate credentials in the provider and update the hosting platform's secret manager. Do not copy secrets into a ZIP, Git repository, or public hosting directory.
