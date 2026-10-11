import urllib.request
from bs4 import BeautifulSoup
import re, json, time
import yfinance as yf
import pandas as pd
import numpy as np

def clean_val(v):
    if not v: return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try: return float(v)
    except: return 0.0

def fetch_screener(sym):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    html = ''
    for suffix in ['/consolidated/', '/']:
        url = f'https://www.screener.in/company/{sym}{suffix}'
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                text = resp.read().decode('utf-8')
                if 'Market Cap' in text:
                    html = text
                    break
        except Exception:
            continue
    if not html:
        return {'symbol': sym, 'error': 'not_found'}
        
    soup = BeautifulSoup(html, 'html.parser')
    res = {'symbol': sym}
    top = soup.find('ul', id='top-ratios')
    if top:
        for li in top.find_all('li'):
            text = li.get_text(' ', strip=True)
            if 'Market Cap' in text:
                m = re.search(r'Market Cap.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['mcap'] = clean_val(m.group(1))
            elif 'Current Price' in text:
                m = re.search(r'Current Price.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['cmp'] = clean_val(m.group(1))
            elif 'High / Low' in text:
                m = re.search(r'High / Low.*?([\d,]+(?:\.\d+)?)\s*/\s*([\d,]+(?:\.\d+)?)', text)
                if m:
                    res['high_52w'] = clean_val(m.group(1))
                    res['low_52w'] = clean_val(m.group(2))
            elif 'Stock P/E' in text:
                m = re.search(r'Stock P/E.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['pe'] = clean_val(m.group(1))
            elif 'ROCE' in text:
                m = re.search(r'ROCE.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['roce'] = clean_val(m.group(1))
            elif 'ROE' in text:
                m = re.search(r'ROE.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['roe'] = clean_val(m.group(1))
    
    # Balance sheet
    borrowings = 0.0
    equity = 0.0
    reserves = 0.0
    bs = soup.find('section', id='balance-sheet')
    if bs:
        for tr in bs.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds:
                if 'Borrowings' in tds[0]: borrowings = clean_val(tds[-1])
                elif 'Equity Capital' in tds[0]: equity = clean_val(tds[-1])
                elif 'Reserves' in tds[0]: reserves = clean_val(tds[-1])
    net_worth = equity + reserves
    res['borrowings'] = borrowings
    res['net_worth'] = net_worth
    res['de_ratio'] = round(borrowings / net_worth, 2) if net_worth > 0 else 0.0

    # Shareholding
    prom_hold = 0.0
    pledge_pct = 0.0
    sh = soup.find('section', id='shareholding')
    if sh:
        for tr in sh.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and 'Promoters' in tds[0]:
                prom_hold = clean_val(tds[-1])
            text = tr.get_text()
            if 'Pledged' in text:
                m = re.search(r'([\d\.]+)%', text)
                if m: pledge_pct = float(m.group(1))
    res['promoter_holding'] = prom_hold
    res['pledged_pct'] = pledge_pct

    # CFO and PAT
    cfo = 0.0
    cf = soup.find('section', id='cash-flow')
    if cf:
        for tr in cf.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and 'Cash from Operating Activity' in tds[0]:
                cfo = clean_val(tds[-1])
    res['cfo'] = cfo

    annual_pat = 0.0
    pnl = soup.find('section', id='profit-loss')
    if pnl:
        for tr in pnl.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and tds[0] == 'Net Profit' and len(tds) >= 2:
                annual_pat = clean_val(tds[-2])
    res['annual_pat'] = annual_pat
    res['cfo_pat'] = round(cfo / annual_pat, 2) if annual_pat > 0 else 0.0

    return res

test_tickers = [
    ('ACE', 'ACE.NS', 'Action Construction Equipment', 'Cranes & Construction Equipment'),
    ('NEWGEN', 'NEWGEN.NS', 'Newgen Software Technologies', 'Enterprise Software & Banking Automation'),
    ('AHLUCONT', 'AHLUCONT.NS', 'Ahluwalia Contracts (India)', 'Institutional & Urban Infra EPC'),
    ('GARFIBRES', 'GARFIBRES.NS', 'Garware Technical Fibres', 'Technical Textiles & Aquaculture Nets'),
    ('MANORAMA', 'MANORAMA.NS', 'Manorama Industries', 'Cocoa Butter Equivalents & Specialty Fats'),
    ('GULFOILLUB', 'GULFOILLUB.NS', 'Gulf Oil Lubricants India', 'Auto/EV Lubricants & Fluid Tech'),
    ('ZENSARTECH', 'ZENSARTECH.NS', 'Zensar Technologies', 'Digital Engineering & AI Services'),
    ('SOTL', 'SOTL.NS', 'Savita Oil Technologies', 'Transformer Oils & Speciality Petroleum'),
    ('DPABHUSHAN', 'DPABHUSHAN.NS', 'D.P. Abhushan', 'Jewellery Retail & Gold Hedging'),
    ('FOSECOIND', 'FOSECOIND.NS', 'Foseco India', 'Foundry Metallurgy & High-Temp Chemicals'),
    ('SALZERELEC', 'SALZERELEC.NS', 'Salzer Electronics', 'Industrial Switchgear & Wire Harnesses'),
    ('GABRIEL', 'GABRIEL.NS', 'Gabriel India', 'Ride Control & Auto Suspensions')
]

out = []
for sym, yf_sym, name, sector in test_tickers:
    time.sleep(1.5)
    try:
        d = fetch_screener(sym)
        d['name'] = name
        d['sector'] = sector
        d['yf_sym'] = yf_sym
        
        # Yahoo finance technicals
        tk = yf.Ticker(yf_sym)
        hist = tk.history(period='6mo')
        rsi = 50.0
        if len(hist) > 15:
            delta = hist['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = round(float(100 - (100 / (1 + rs)).iloc[-1]), 1)
        d['rsi'] = rsi
        out.append(d)
        print(f"{sym:<12}: MCap={d.get('mcap')} Cr | CMP={d.get('cmp')} | PE={d.get('pe')} | ROCE={d.get('roce')}% | D/E={d.get('de_ratio')} | Prom={d.get('promoter_holding')}% | Pledg={d.get('pledged_pct')}% | CFO/PAT={d.get('cfo_pat')} | RSI={rsi}")
    except Exception as e:
        print(f"{sym}: error {e}")

with open('screened_expansion_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print("Done. Saved to screened_expansion_candidates.json")
