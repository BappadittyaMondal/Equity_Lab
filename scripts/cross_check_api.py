import json
import os
import re

with open('docs/api_contract.json', 'r', encoding='utf-8') as f:
    spec = json.load(f)

backend_endpoints = sorted(list(spec.get('paths', {}).keys()))

js_dir = 'frontend_deploy/js'
frontend_urls = set()

for root, dirs, files in os.walk(js_dir):
    for file in files:
        if file.endswith('.js'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'["\'](/api/[a-zA-Z0-9_\-/{}]+|/health|/docs)["\']', content)
                for m in matches:
                    frontend_urls.add(m)

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
    # check if fe matches any backend endpoint pattern
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
