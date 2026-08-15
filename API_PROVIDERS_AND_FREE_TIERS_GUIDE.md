# API Keys & Multi-LLM Provider Guide (Indian Equity Cash Market)

**Focus Area:** Long-Term Investment, Multibagger Discovery, Swing Trading, Fundamental Deep Dives (Spot Cash Market Only — **No Options Trading**).

---

## 1. Provider Configuration Status

The configuration file contains placeholders for several providers, but the current executable service invokes **Gemini only**. Do not represent unimplemented providers as available until they have their own tested integrations.

| LLM Provider | Current runtime status | Notes |
| :--- | :--- | :---: | :--- |
| **Google Gemini** | Implemented | Uses the configured Gemini model when a valid key is present. |
| **Groq AI** | Placeholder only | Configuration field exists; no runtime client is implemented. |
| **DeepSeek AI** | Placeholder only | Configuration field exists; no runtime client is implemented. |
| **Moonshot Kimi AI** | Not configured | No environment field or runtime client is implemented. |
| **Anthropic Claude** | Placeholder only | Configuration field exists; no runtime client is implemented. |
| **OpenAI** | Not configured | No environment field or runtime client is implemented. |

---

## 2. 100% FREE Market Data & Fundamental APIs (Spot Equity Market)

You do **NOT** need to pay thousands of rupees for data feeds. Here are the top 100% FREE APIs tailored for Indian cash equity:

### A. Python `yfinance` Library (100% FREE, No API Key Required)
* **What it provides:** 15+ years of daily OHLCV prices, volume, split/bonus history, and key balance sheet ratios for all NSE (`.NS`) and BSE (`.BO`) stocks.
* **Cost:** 100% Free, zero setup needed.

### B. Angel One SmartAPI (100% FREE for Market Data)
* **What it provides:** Official NSE/BSE tick data, historical 1-minute to daily candles, and delivery data.
* **How to get it:** Register at [Angel One SmartAPI Portal](https://smartapi.angelone.in/), create a free developer account.
* **Cost:** 100% Free.

### C. DhanHQ API (100% FREE for Account Holders)
* **What it provides:** Real-time cash market quotes, historical charts, and portfolio data.
* **How to get it:** Generate access token directly from Dhan web app settings.
* **Cost:** 100% Free.

### D. Alpha Vantage API (FREE Tier - 25 Calls/Day)
* **What it provides:** Daily equity prices, RSI, MACD, and moving average technical indicator series.
* **How to get it:** Claim free API key instantly at [Alpha Vantage](https://www.alphavantage.co/support/#api-key).
* **Cost:** Free (25 API requests/day).

### E. NewsAPI (FREE Tier - 100 Requests/Day)
* **What it provides:** Corporate news updates, management interview alerts, and industry scuttlebutt.
* **How to get it:** Register free at [NewsAPI.org](https://newsapi.org/).
* **Cost:** Free for non-commercial/developer use.

---

## 3. Step-by-Step: How to Get Your FREE AI API Keys

### Step 1: Get Google Gemini API Key (FREE)
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API Key"** -> **"Create API Key in new project"**.
4. Copy your key into `API_KEYS_CONFIG.env` under `GEMINI_API_KEY=`.

### Step 2: Get Groq API Key (FREE)
1. Go to [Groq Console](https://console.groq.com/).
2. Sign up with Google/GitHub.
3. Click **"API Keys"** -> **"Create API Key"**.
4. Copy your key into `API_KEYS_CONFIG.env` under `GROQ_API_KEY=`.

### Step 3: Get DeepSeek API Key
1. Go to [DeepSeek Platform](https://platform.deepseek.com/).
2. Create an account (comes with free initial trial credits).
3. Generate API Key under **API Keys** tab and paste into `DEEPSEEK_API_KEY=`.

### Step 4: Get Kimi (Moonshot AI) API Key
1. Go to [Moonshot AI Platform](https://platform.moonshot.cn/).
2. Register an account to receive developer access tokens.
3. Paste key into `KIMI_MOONSHOT_API_KEY=`.

---

## 4. Configuration File Created in Workspace

We have created two environment configuration files in your repository:
1. `API_KEYS_CONFIG.env` — Master API configuration template.
2. `.env.example` — Standard environment key file.

To activate your keys:
1. Open `API_KEYS_CONFIG.env` in your editor.
2. Paste your real API keys into the corresponding fields.
3. Set `ACTIVE_LLM_PROVIDER=gemini` (or `groq`, `deepseek`, `kimi`, `claude`, `openai`) to select your default AI provider.
