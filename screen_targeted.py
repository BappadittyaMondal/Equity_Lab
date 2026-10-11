import urllib.request
from bs4 import BeautifulSoup
import re, json, time
import yfinance as yf
import numpy as np

targets = [
    ('RITES', '/company/RITES/consolidated/', 'RITES.NS', 'Rail Infra Consultancy & Rolling Stock Exports'),
    ('CYIENTDLM', '/company/CYIENTDLM/consolidated/', 'CYIENTDLM.NS', 'Electronic Manufacturing Services / Avionics & Defense'),
    ('DATAPATTNS', '/company/DATAPATTNS/', 'DATAPATTNS.NS', 'Defense & Aerospace Electronics / Radars & EW Systems'),
    ('SANSERA', '/company/SANSERA/', 'SANSERA.NS', 'Precision Forged & Machined Components / Aero & Defense'),
    ('MPSLTD', '/company/MPSLTD/consolidated/', 'MPSLTD.NS', 'Digital Publishing & Learning AI Platforms'),
    ('WONDERLA', '/company/WONDERLA/', 'WONDERLA.NS', 'Amusement Parks & Experiential Leisure Infra'),
    ('FINEORG', '/company/FINEORG/consolidated/', 'FINEORG.NS', 'Specialty Oleochemical Additives / Polymer & Food'),
    ('SUPRAJIT', '/company/SUPRAJIT/consolidated/', 'SUPRAJIT.NS', 'Auto Control Cables & LED Actuation Systems'),
    ('GABRIEL', '/company/GABRIEL/consolidated/', 'GABRIEL.NS', 'Ride Control Products & EV Shock Absorbers'),
    ('CIGNITITEC', '/company/CIGNITITEC/consolidated/', 'CIGNITITEC.NS', 'AI & Digital Assurance Engineering'),
    ('SONATSOFTW', '/company/SONATSOFTW/consolidated/', 'SONATSOFTW.NS', 'Enterprise Cloud & Modernization Services')
]

def clean_val(v):
    if not v: return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try: return float(v)
    except: return 0.0

headers = {'User-Agent': 'Mozilla/5.0'}
results = []

for s, url_path, yf_sym, sec in targets:
    time.sleep(0.8)
    url = f'https://www.screener.in{url_path}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f'{s}: failed to fetch {e}')
        continue

    soup = BeautifulSoup(html, 'html.parser')
    res = {'symbol': s, 'url_path': url_path, 'yf_sym': yf_sym, 'sector': sec}
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
            elif 'Stock P/E' in text:
                m = re.search(r'Stock P/E.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['pe'] = clean_val(m.group(1))
            elif 'ROCE' in text:
                m = re.search(r'ROCE.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['roce'] = clean_val(m.group(1))
            elif 'ROE' in text:
                m = re.search(r'ROE.*?([\d,]+(?:\.\d+)?)', text)
                if m: res['roe'] = clean_val(m.group(1))

    # BS
    borr, eq, resv = 0.0, 0.0, 0.0
    bs = soup.find('section', id='balance-sheet')
    if bs:
        for tr in bs.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds:
                if 'Borrowings' in tds[0]: borr = clean_val(tds[-1])
                elif 'Equity Capital' in tds[0]: eq = clean_val(tds[-1])
                elif 'Reserves' in tds[0]: resv = clean_val(tds[-1])
    nw = eq + resv
    res['de'] = round(borr / nw, 2) if nw > 0 else 0.0

    # Shareholding
    prom, pl = 0.0, 0.0
    sh = soup.find('section', id='shareholding')
    if sh:
        for tr in sh.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and 'Promoters' in tds[0]: prom = clean_val(tds[-1])
            t = tr.get_text()
            if 'Pledged' in t:
                m = re.search(r'([\d\.]+)%', t)
                if m: pl = float(m.group(1))
    res['prom'] = prom
    res['pledge'] = pl

    # CFO
    cfo = 0.0
    cf = soup.find('section', id='cash-flow')
    if cf:
        for tr in cf.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and ('Cash from Operating' in tds[0] or 'Operating Activity' in tds[0]):
                cfo = clean_val(tds[-1])
    res['cfo'] = cfo

    pat = 0.0
    pnl = soup.find('section', id='profit-loss')
    if pnl:
        for tr in pnl.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and tds[0] == 'Net Profit' and len(tds) >= 2:
                pat = clean_val(tds[-2])
    res['pat'] = pat
    res['cfo_pat'] = round(cfo / pat, 2) if pat > 0 else 0.0

    # RSI
    rsi = 50.0
    try:
        tk = yf.Ticker(yf_sym)
        hist = tk.history(period='3mo')
        if len(hist) > 15:
            delta = hist['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = round(float(100 - (100 / (1 + rs)).iloc[-1]), 1)
    except: pass
    res['rsi'] = rsi

    mcap = res.get('mcap', 0)
    roce = res.get('roce', 0)
    de = res.get('de', 0)
    pledge = res.get('pledge', 0)
    cfo_pat = res.get('cfo_pat', 0)
    pe = res.get('pe', 0)

    # Let's check pass conditions
    is_pass = (500 <= mcap <= 15000) and (roce >= 20.0) and (de <= 0.35) and (pledge <= 3.5) and (prom >= 40.0) and (cfo > 0)
    status = 'PASS' if is_pass else 'FAIL'
    print(f"{s:<12}: MCap={mcap:6.0f} | ROCE={roce:4.1f}% | D/E={de:4.2f} | Prom={prom:4.1f}% | Pledg={pledge:4.1f}% | CFO={cfo:5.0f} Cr | PAT={pat:5.0f} Cr | CFO/PAT={cfo_pat:4.2f} | PE={pe:4.1f} | RSI={rsi:4.1f} -> {status}")
    res['status'] = status
    results.append(res)

with open('targeted_screen_results.json', 'w') as f:
    json.dump(results, f, indent=2)
