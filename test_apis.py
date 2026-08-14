import os
import sys
import requests
import json

def load_env(env_path):
    env_vars = {}
    if not os.path.exists(env_path):
        return env_vars
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()
    return env_vars

def main():
    env = load_env('API_KEYS_CONFIG.env')
    print("=" * 70)
    print("IERL AI EQUITY OS - API CONNECTIVITY & VALIDATION REPORT")
    print("=" * 70)
    
    # 1. Test Google Gemini API
    gemini_key = env.get('GEMINI_API_KEY', '')
    print("\n[1] Testing Google Gemini API...")
    if not gemini_key or 'your_' in gemini_key:
        print(" -> STATUS: NOT CONFIGURED (Missing Key)")
    else:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                models = res.json().get('models', [])
                model_names = [m.get('name', '') for m in models[:3]]
                print(f" -> STATUS: SUCCESS (200 OK) | Verified Models: {len(models)} available")
            else:
                print(f" -> STATUS: FAILED (HTTP {res.status_code}) - {res.text[:100]}")
        except Exception as e:
            print(f" -> STATUS: ERROR - {e}")

    # 2. Test Groq API
    groq_key = env.get('GROQ_API_KEY', '')
    print("\n[2] Testing Groq API...")
    if not groq_key or 'your_' in groq_key:
        print(" -> STATUS: NOT CONFIGURED (Missing Key)")
    else:
        try:
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {groq_key}"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                models = res.json().get('data', [])
                print(f" -> STATUS: SUCCESS (200 OK) | Available Models: {len(models)}")
            else:
                print(f" -> STATUS: FAILED (HTTP {res.status_code}) - {res.text[:100]}")
        except Exception as e:
            print(f" -> STATUS: ERROR - {e}")

    # 3. Test Yahoo Finance (yfinance)
    print("\n[3] Testing Yahoo Finance (yfinance)...")
    try:
        import yfinance as yf
        ticker = yf.Ticker("RELIANCE.NS")
        hist = ticker.history(period="5d")
        if not hist.empty:
            last_price = hist['Close'].iloc[-1]
            print(f" -> STATUS: SUCCESS | Fetched RELIANCE.NS last price: INR {last_price:.2f}")
        else:
            print(" -> STATUS: WARNING (Returned empty dataframe)")
    except ImportError:
        print(" -> STATUS: NOT INSTALLED (Package 'yfinance' missing. Installing...)")
    except Exception as e:
        print(f" -> STATUS: ERROR - {e}")

    # 4. Test Alpha Vantage API
    av_key = env.get('ALPHA_VANTAGE_API_KEY', '')
    print("\n[4] Testing Alpha Vantage API...")
    if not av_key or 'your_' in av_key:
        print(" -> STATUS: NOT CONFIGURED (Default placeholder in file)")
    else:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=RELIANCE.BSE&apikey={av_key}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and "Global Quote" in res.text:
                print(" -> STATUS: SUCCESS (200 OK)")
            else:
                print(f" -> STATUS: RESPONSE - {res.text[:100]}")
        except Exception as e:
            print(f" -> STATUS: ERROR - {e}")

    # 5. Test Angel One SmartAPI Credentials
    angel_key = env.get('ANGELONE_SMART_API_KEY', '')
    angel_code = env.get('ANGELONE_CLIENT_CODE', '')
    angel_pass = env.get('ANGELONE_PASSWORD', '')
    angel_totp = env.get('ANGELONE_TOTP_SECRET', '')
    print("\n[5] Testing Angel One SmartAPI Configuration...")
    print(f" -> API Key: {'Configured (' + angel_key + ')' if angel_key and 'your_' not in angel_key else 'Missing'}")
    print(f" -> Client Code: {'Configured (' + angel_code + ')' if angel_code and 'your_' not in angel_code else 'Missing'}")
    print(f" -> Password: {'Configured (Set)' if angel_pass and 'your_' not in angel_pass else 'Missing'}")
    print(f" -> TOTP Secret: {'Configured' if angel_totp and 'your_' not in angel_totp else 'NOT CONFIGURED (Required for automated login)'}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
