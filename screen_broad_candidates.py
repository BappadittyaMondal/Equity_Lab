import urllib.request
from bs4 import BeautifulSoup
import re, json, time

syms = [
    'BANCOINDIA', 'TDPOWERSYS', 'SANGHVI', 'DYNAMATECH', 'HARSHA', 
    'MPSLTD', 'CIGNITITEC', 'SONATSOFTW', 'WONDERLA', 'DIVGIITTS',
    'GABRIEL', 'SANDHAR', 'SUBROS', 'ROSSARI', 'HLEGLAS',
    'AVALON', 'CYIENTDLM', 'DATAPATTNS', 'DCXINDIA', 'GRAVITA'
]

def clean_val(v):
    if not v: return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try: return float(v)
    except: return 0.0

headers = {'User-Agent': 'Mozilla/5.0'}
passed = []

for s in syms:
    time.sleep(0.5)
    html = ''
    for path in [f'/company/{s}/consolidated/', f'/company/{s}/']:
        try:
            req = urllib.request.Request(f'https://www.screener.in{path}', headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                text = resp.read().decode('utf-8')
                if 'Market Cap' in text:
                    html = text
                    break
        except: pass
    if not html: continue
    
    soup = BeautifulSoup(html, 'html.parser')
    res = {'symbol': s}
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
            if tds and 'Cash from Operating Activity' in tds[0]: cfo = clean_val(tds[-1])
    res['cfo'] = cfo

    pat = 0.0
    pnl = soup.find('section', id='profit-loss')
    if pnl:
        for tr in pnl.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and tds[0] == 'Net Profit' and len(tds) >= 2: pat = clean_val(tds[-2])
    res['pat'] = pat
    res['cfo_pat'] = round(cfo / pat, 2) if pat > 0 else 0.0

    mcap = res.get('mcap', 0)
    roce = res.get('roce', 0)
    de = res.get('de', 0)
    pledge = res.get('pledge', 0)
    cfo_pat = res.get('cfo_pat', 0)
    pe = res.get('pe', 0)

    is_pass = (500 <= mcap <= 15000) and (roce >= 20.0) and (de <= 0.35) and (pledge <= 3.5) and (cfo_pat > 0)
    status = 'PASS' if is_pass else 'FAIL'
    print(f"{s:<12}: MCap={mcap:6.0f} | ROCE={roce:4.1f}% | D/E={de:4.2f} | Prom={prom:4.1f}% | Pledg={pledge:4.1f}% | CFO/PAT={cfo_pat:4.2f} | PE={pe:4.1f} -> {status}")
    if is_pass: passed.append(res)

print('\nPASSED CANDIDATES:')
for p in passed:
    print(p)

with open('broad_screened_passed.json', 'w') as f:
    json.dump(passed, f, indent=2)
