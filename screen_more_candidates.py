import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np
import json
import re
import time

test_tickers = [
    {'sym': 'UNIPARTS', 'yf': 'UNIPARTS.NS', 'theme': 'Off-Highway & Agri Mechanical Systems / Global Export'},
    {'sym': 'STEELCAS', 'yf': 'STEELCAS.NS', 'theme': 'Heavy Steel Castings / Locomotives, Mining & Defense'},
    {'sym': 'SHIVALIK', 'yf': 'SBCL.NS', 'theme': 'Bimetal & Shunt Resistors / EV & Smart Meter Energy Components'},
    {'sym': 'RACLGEAR', 'yf': 'RACLGEAR.BO', 'theme': 'Precision Gears & Shafts / European Luxury 2W & EV OEMs'},
    {'sym': 'SALZERELEC', 'yf': 'SALZERELEC.NS', 'theme': 'Industrial Switchgear / EV Contactors & Wire Harnesses'},
    {'sym': 'GABRIEL', 'yf': 'GABRIEL.NS', 'theme': 'Ride Control & Suspension / 2W/4W EV & Sunroof Systems'},
    {'sym': 'CONTROLPR', 'yf': 'CONTROLPR.NS', 'theme': 'Industrial Coding & Marking Systems / Track & Trace Monopoly'},
    {'sym': 'FOSECOIND', 'yf': 'FOSECOIND.NS', 'theme': 'Foundry Metallurgy Chemicals / Defense & Auto Casting Moat'},
    {'sym': 'THEMISMED', 'yf': 'THEMISMED.NS', 'theme': 'Critical Care & Anesthesia Injectables / Hospital API Chains'},
    {'sym': 'CYIENTDLM', 'yf': 'CYIENTDLM.NS', 'theme': 'Electronic Manufacturing Services / Aerospace & Defense Avionics'},
    {'sym': 'DCXINDIA', 'yf': 'DCXINDIA.NS', 'theme': 'Defense Electronic Sub-systems / Cable Harnesses & Offsets'},
    {'sym': 'GRAVITA', 'yf': 'GRAVITA.NS', 'theme': 'Circular Economy / Lead, Aluminum & Lithium Battery Recycling'},
    {'sym': 'GENUSPOWER', 'yf': 'GENUSPOWER.NS', 'theme': 'Smart Electricity Meters / RDSS National Grid Mandate'},
    {'sym': 'AVANTIFEED', 'yf': 'AVANTIFEED.NS', 'theme': 'Aquaculture Feed & Seafood Processing / Cash-Rich Debt-Free'},
    {'sym': 'FINEORG', 'yf': 'FINEORG.NS', 'theme': 'Oleochemical Green Additives / Food & Polymer Processing Moat'},
    {'sym': 'SUPRAJIT', 'yf': 'SUPRAJIT.NS', 'theme': 'Mechanical Control Cables & Halogen/LED Auto Lamps'}
]

def clean_val(v):
    if not v:
        return 0.0
    v = str(v).replace(',', '').replace('%', '').replace('₹', '').strip()
    try:
        return float(v)
    except:
        return 0.0

def fetch_screener_simple(sym):
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
                if m: res['screener_cmp'] = clean_val(m.group(1))
            elif 'High / Low' in text:
                m = re.search(r'High / Low.*?([\d,]+(?:\.\d+)?)\s*/\s*([\d,]+(?:\.\d+)?)', text)
                if m:
                    res['52w_high'] = clean_val(m.group(1))
                    res['52w_low'] = clean_val(m.group(2))
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
    res['borrowings'] = borrowings
    res['net_worth'] = net_worth
    res['de_ratio'] = round(borrowings / net_worth, 2) if net_worth > 0 else 0.0

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

    return res

results = []
for c in test_tickers:
    time.sleep(2.0)
    try:
        data = fetch_screener_simple(c['sym'])
        data.update(c)
        print(f"{c['sym']:<12}: MCap={data.get('mcap')} Cr, PE={data.get('pe')}, ROCE={data.get('roce')}%, D/E={data.get('de_ratio')}, CFO/PAT={data.get('cfo_pat')}, PromHold={data.get('promoter_holding')}%, Pledge={data.get('pledged_pct')}%")
        results.append(data)
    except Exception as e:
        print(f"Failed {c['sym']}: {e}")

with open('screened_candidates_raw.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
