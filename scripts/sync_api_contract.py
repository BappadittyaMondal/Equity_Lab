# -*- coding: utf-8 -*-
import sys
import json
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from app.main import app

schema = app.openapi()

contract_path = base_dir / "docs" / "api_contract.json"
with open(contract_path, "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2)

ops = sum(
    1
    for p, methods in schema.get("paths", {}).items()
    for m in methods
    if m.lower() in ["get", "post", "put", "delete", "patch"]
)

freeze_path = base_dir / "docs" / "API_CONTRACT_FREEZE.md"
if freeze_path.exists():
    txt = freeze_path.read_text(encoding="utf-8")
    txt2 = re.sub(r"Total Backend Endpoints\*\*: \d+", f"Total Backend Endpoints**: {ops}", txt)
    freeze_path.write_text(txt2, encoding="utf-8")

print(f"[SUCCESS] Updated api_contract.json & API_CONTRACT_FREEZE.md with {ops} operations.")
