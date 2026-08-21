import json
import os
import re

with open('docs/api_contract.json', 'r', encoding='utf-8') as f:
    spec = json.load(f)

backend_endpoints = sorted(list(spec.get('paths', {}).keys()))

frontend_dir = 'frontend_deploy'
frontend_urls = set()
raw_matches = set()

# Enhanced regex to capture template literals, f-strings, API_BASE prefixes, and variables
pattern = re.compile(r'[`"\'](?:\$\{API_BASE\}|http://[a-zA-Z0-9.:]+)?(/api/v1/[a-zA-Z0-9_\-/${}()+.,:=%]+|/health|/docs)[`"\']')

for root, dirs, files in os.walk(frontend_dir):
    if 'archive' in root:
        continue
    for file in files:
        if file.endswith('.js') or file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                found = pattern.findall(content)
                for m in found:
                    raw_matches.add(m)
                    # Clean query strings
                    cleaned = m.split('?')[0]
                    # Normalize JS template string variables to standard OpenAPI placeholders
                    normalized = re.sub(r'\$\{\s*(?:encodeURIComponent\()?([a-zA-Z0-9_.]+)\)?\s*\}', r'{\1}', cleaned)
                    # Normalize standard variable names to match schema parameters
                    normalized = re.sub(r'\{[a-zA-Z0-9_.]*symbol[a-zA-Z0-9_.]*\}', '{symbol}', normalized, flags=re.IGNORECASE)
                    normalized = re.sub(r'\{[a-zA-Z0-9_.]*strategy[a-zA-Z0-9_.]*\}', '{strategy_id}', normalized, flags=re.IGNORECASE)
                    frontend_urls.add(normalized)

print(f"Backend Endpoints Count: {len(backend_endpoints)}")
print(f"Frontend Endpoints Referenced: {len(frontend_urls)}")

print("\n--- All Backend Endpoints ---")
for ep in backend_endpoints:
    methods = list(spec['paths'][ep].keys())
    print(f"  {ep} [{', '.join(methods).upper()}]")

print("\n--- Frontend Referenced Endpoints ---")
for url in sorted(frontend_urls):
    print(f"  {url}")

missing_in_backend = []
for fe in frontend_urls:
    fe_clean = fe.split('?')[0]
    matched = any(fe_clean == be or fe_clean.startswith(be.split('{')[0]) for be in backend_endpoints)
    if not matched:
        missing_in_backend.append(fe)

print("\n--- Frontend Calls Missing in Backend Spec ---")
if missing_in_backend:
    for m in missing_in_backend:
        print(f"  ❌ {m}")
else:
    print("  None! All frontend API calls map to valid backend endpoints.")

uncalled_backend = []
for be in backend_endpoints:
    prefix = be.split('{')[0]
    matched = any(fe == be or fe.startswith(prefix) for fe in frontend_urls)
    if not matched:
        uncalled_backend.append(be)

print("\n--- Backend Endpoints NOT Yet Integrated in Frontend ---")
for ub in uncalled_backend:
    print(f"  - {ub}")
