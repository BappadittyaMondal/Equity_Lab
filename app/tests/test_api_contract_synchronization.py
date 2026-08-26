"""Test API Contract Synchronization.

Fails if app endpoints, docs/api_contract.json, or docs/API_CONTRACT_FREEZE.md ever diverge.
"""

import json
import re
from pathlib import Path
from app.main import app

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONTRACT_JSON = BASE_DIR / "docs" / "api_contract.json"
FREEZE_MD = BASE_DIR / "docs" / "API_CONTRACT_FREEZE.md"


def test_api_contract_synchronization():
    # 1. Extract operations from FastAPI openapi schema
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})
    actual_ops = sum(
        1
        for path, methods in paths.items()
        for method in methods
        if method.lower() in ["get", "post", "put", "delete", "patch"]
    )

    # 2. Check docs/api_contract.json
    assert CONTRACT_JSON.exists(), "docs/api_contract.json must exist"
    contract_data = json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))
    contract_ops = sum(
        1
        for path, methods in contract_data.get("paths", {}).items()
        for method in methods
        if method.lower() in ["get", "post", "put", "delete", "patch"]
    )
    assert contract_ops == actual_ops, f"docs/api_contract.json ({contract_ops}) diverges from FastAPI OpenAPI schema ({actual_ops})"

    # 3. Check docs/API_CONTRACT_FREEZE.md
    assert FREEZE_MD.exists(), "docs/API_CONTRACT_FREEZE.md must exist"
    freeze_text = FREEZE_MD.read_text(encoding="utf-8")
    match = re.search(r"Total Backend Endpoints\*\*: (\d+)", freeze_text)
    assert match is not None, "Could not parse Total Backend Endpoints from API_CONTRACT_FREEZE.md"
    freeze_count = int(match.group(1))
    assert freeze_count == actual_ops, f"docs/API_CONTRACT_FREEZE.md ({freeze_count}) diverges from actual OpenAPI schema ({actual_ops})"

    # 4. Check @router.* decorators in app/api/*.py
    decorator_count = 0
    for py_file in (BASE_DIR / "app" / "api").rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"@router\.(get|post|put|delete|patch)", text)
        decorator_count += len(matches)

    assert decorator_count == actual_ops, f"Decorator count in app/api/*.py ({decorator_count}) diverges from FastAPI OpenAPI schema ({actual_ops})"
