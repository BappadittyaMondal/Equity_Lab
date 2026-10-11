import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup
import yfinance as yf
import json
import re
import time

test_syms = [
    {'sym': 'ACE', 'yf': 'ACE.NS', 'name': 'Action Construction Equipment'},
    {'sym': 'HGINFRA', 'yf': 'HGINFRA.NS', 'name': 'H.G. Infra Engineering'},
    {'sym': 'AHLUCONT', 'yf': 'AHLUCONT.NS', 'name': 'Ahluwalia Contracts'},
    {'sym': 'MANINFRA', 'yf': 'MANINFRA.NS', 'name': 'Man Infraconstruction'},
    {'sym': 'RKFORGE', 'yf': 'RKFORGE.NS', 'name': 'Ramkrishna Forgings'},
    {'sym': 'JUPITERWAG', 'yf': 'JUPITERWAG.NS', 'name': 'Jupiter Wagons'},
    {'sym': 'TITAGARH', 'yf': 'TITAGARH.NS', 'name': 'Titagarh Rail Systems'},
    {'sym': 'MTARTECH', 'yf': 'MTARTECH.NS', 'name': 'MTAR Technologies'},
    {'sym': 'PARAS', 'yf': 'PARAS.NS', 'name': 'Paras Defence'},
    {'sym': 'EMUDHRA', 'yf': 'EMUDHRA.NS', 'name': 'eMudhra Ltd'},
    {'sym': 'MAPMYINDIA', 'yf': 'MAPMYINDIA.NS', 'name': 'C.E. Info Systems'},
    {'sym': 'NEWGEN', 'yf': 'NEWGEN.NS', 'name': 'Newgen Software Technologies'},
    {'sym': 'MASTEK', 'yf': 'MASTEK.NS', 'name': 'Mastek Ltd'},
    {'sym': 'RATEGAIN', 'yf': 'RATEGAIN.NS', 'name': 'RateGain Travel Tech'},
    {'sym': 'KNRCON', 'yf': 'KNRCON.NS', 'name': 'KNR Constructions'}
]

def clean_val(v):
    if not v:
        return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try:
        return float(v)
    except:
        return 0.0

def fetch_screener(sym):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f'https://www.screener.in/company/{sym}/consolidated/'
    html = ''
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8')
    except Exception:
        url = f'https://www.screener.in/company/{sym}/'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    res = {'symbol': sym}

    top_ratios = soup.find('ul', id='top-ratios')
    if top_ratios:
        for li in top_ratios.find_all('li'):
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

    borrowings = 0.0
    equity = 0.0
    reserves = 0.0
    bs = soup.find('section', id='balance-sheet')
    if bs:
        for tr in bs.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds:
                if 'Borrowings' in tds[0]:
                    borrowings = clean_val(tds[-1])
                elif 'Equity Capital' in tds[0]:
                    equity = clean_val(tds[-1])
                elif 'Reserves' in tds[0]:
                    reserves = clean_val(tds[-1])
    net_worth = equity + reserves
    res['de_ratio'] = round(borrowings / net_worth, 2) if net_worth > 0 else 0.0

    pledged_pct = 0.0
    promoter_holding = 0.0
    sh = soup.find('section', id='shareholding')
    if sh:
        for tr in sh.find_all('tr'):
            tds = [t.get_text(strip=True) for t in tr.find_all('td')]
            if tds and 'Promoters' in tds[0]:
                promoter_holding = clean_val(tds[-1])
            text = tr.get_text()
            if 'Pledged' in text:
                m = re.search(r'([\d\.]+)%', text)
                if m:
                    pledged_pct = float(m.group(1))
    res['promoter_holding'] = promoter_holding
    res['pledged_pct'] = pledged_pct

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

results = []
for item in test_syms:
    time.sleep(2.0)
    try:
        data = fetch_screener(item['sym'])
        data.update(item)
        print(f"{item['sym']:<12}: MCap=₹{data.get('mcap')} Cr, PE={data.get('pe')}, ROCE={data.get('roce')}%, D/E={data.get('de_ratio')}, PromHold={data.get('promoter_holding')}%, Pledge={data.get('pledged_pct')}%, CFO/PAT={data.get('cfo_pat')}")
        results.append(data)
    except Exception as e:
        print(f"Failed {item['sym']}: {e}")

with open('screened_batch2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
