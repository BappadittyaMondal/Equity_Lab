import urllib.request, json, time, re
from bs4 import BeautifulSoup
import yfinance as yf
import numpy as np

headers = {'User-Agent': 'Mozilla/5.0'}

def clean_val(v):
    if not v: return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try: return float(v)
    except: return 0.0

candidates = [
    ('SANGHVIMOV', 'SANGHVIMOV.NS', 'Sanghvi Movers Ltd', 'Heavy Crane Infrastructure'),
    ('KIRLOSENG', 'KIRLOSENG.NS', 'Kirloskar Oil Engines Ltd', 'Power Generation & Industrial Engines'),
    ('APOLLOPIPE', 'APOLLOPIPE.NS', 'Apollo Pipes Ltd', 'Plastic Pipes & Water Infra'),
    ('SUBROS', 'SUBROS.NS', 'Subros Ltd', 'Thermal Management & EV Aircon Systems'),
    ('HLEGLAS', 'HLEGLAS.NS', 'HLE Glascoat Ltd', 'Filtration & Drying Chemical Equipment'),
    ('GULFOILLUB', 'GULFOILLUB.NS', 'Gulf Oil Lubricants India Ltd', 'Auto & Industrial Lubricants'),
    ('DODLA', 'DODLA.NS', 'Dodla Dairy Ltd', 'Value-Added Dairy FMCG')
]

for sym, yf_sym, name, sector in candidates:
    time.sleep(1.0)
    # Search screener URL
    search_url = f'https://www.screener.in/api/company/search/?q={sym}'
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode('utf-8'))
            if not res: continue
            slug = res[0]['url']
    except Exception as e:
        continue

    url = f'https://www.screener.in{slug}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            soup = BeautifulSoup(r.read().decode('utf-8'), 'html.parser')
    except Exception:
        continue

    top = soup.find('ul', id='top-ratios')
    mcap, pe, roce = 0, 0, 0
    if top:
        for li in top.find_all('li'):
            t = li.get_text(' ', strip=True)
            if 'Market Cap' in t:
                m = re.search(r'Market Cap.*?([\d,]+(?:\.\d+)?)', t)
                if m: mcap = clean_val(m.group(1))
            elif 'Stock P/E' in t:
                m = re.search(r'Stock P/E.*?([\d,]+(?:\.\d+)?)', t)
                if m: pe = clean_val(m.group(1))
            elif 'ROCE' in t:
                m = re.search(r'ROCE.*?([\d,]+(?:\.\d+)?)', t)
                if m: roce = clean_val(m.group(1))

    borr, eq, resv = 0.0, 0.0, 0.0
    bs = soup.find('section', id='balance-sheet')
    if bs:
        for tr in bs.find_all('tr'):
            tds = [x.get_text(strip=True) for x in tr.find_all('td')]
            if tds:
                if 'Borrowings' in tds[0]: borr = clean_val(tds[-1])
                elif 'Equity Capital' in tds[0]: eq = clean_val(tds[-1])
                elif 'Reserves' in tds[0]: resv = clean_val(tds[-1])
    nw = eq + resv
    de = round(borr / nw, 2) if nw > 0 else 0.0

    prom, pl = 0.0, 0.0
    sh = soup.find('section', id='shareholding')
    if sh:
        for tr in sh.find_all('tr'):
            tds = [x.get_text(strip=True) for x in tr.find_all('td')]
            if tds and 'Promoters' in tds[0]: prom = clean_val(tds[-1])
            t = tr.get_text()
            if 'Pledged' in t:
                m = re.search(r'([\d\.]+)%', t)
                if m: pl = float(m.group(1))

    cf = soup.find('section', id='cash-flow')
    cfo = 0.0
    if cf:
        for tr in cf.find_all('tr'):
            tds = [x.get_text(strip=True) for x in tr.find_all('td')]
            if tds and ('Operating' in tds[0]): cfo = clean_val(tds[-1])

    is_pass = (500 <= mcap <= 15000) and (roce >= 20.0) and (de <= 0.35) and (pl <= 3.5) and (prom >= 40.0) and (cfo > 0)
    status = 'PASS' if is_pass else 'FAIL'
    print(f'{sym:<12}: MCap={mcap:6.0f} | ROCE={roce:4.1f}% | D/E={de:4.2f} | Prom={prom:4.1f}% | Pledg={pl:4.1f}% | CFO={cfo:5.0f} | PE={pe:4.1f} -> {status}')
