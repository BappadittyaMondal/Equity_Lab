# IERL FastAPI Backend Deployment Guide

This is the FastAPI backend service for the **IERL AI Equity OS**. It handles live market data (`yfinance`), multi-LLM API calls (Gemini, Groq, Claude), and strategy diagnostics.

---

## 🏃 How to Run Locally (Testing on Your PC)

1. Open PowerShell terminal in `d:\bappa_oldPC\Indian_Equity_Project\Equity_final_claude_v_0.3\app`:
```powershell
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
2. Open `http://127.0.0.1:8000/docs` in your browser to view the interactive API documentation.
3. Open `frontend_deploy/index.html` in your browser — it will automatically detect your local backend!

---

## ☁️ How to Deploy Free Cloud Backend (Render.com)

1. Create a free account at [Render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (or upload the `app` folder).
4. Set:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r app/requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = your Google Gemini API key
   - `ACTIVE_LLM_PROVIDER` = `gemini`
6. Click **Deploy Web Service** — Render will give you a free URL (e.g., `https://ierl-backend.onrender.com`).
7. Update `BACKEND_API_URL` in `index.html` on your Hostinger File Manager to point to your Render URL!
