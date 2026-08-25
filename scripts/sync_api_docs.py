"""Synchronize human-facing API documentation files with docs/api_contract.json."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACT_PATH = BASE_DIR / "docs" / "api_contract.json"
DOC_PATH = BASE_DIR / "API_DOCUMENTATION.md"
SURFACE_PATH = BASE_DIR / "API_SURFACE.md"

def sync():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    paths = contract.get("paths", {})

    doc_lines = [
        "# Equity Lab — Complete API Surface Documentation",
        "",
        "> **Version:** 1.0.0  ",
        f"> **Source of Truth:** `docs/api_contract.json`  ",
        f"> **Total Endpoints:** {len(paths)}",
        "",
        "---",
        "",
        "## Endpoint Catalog",
        ""
    ]

    surface_lines = [
        "# Equity Lab — API Surface Specification",
        "",
        f"> Total Endpoints: {len(paths)}",
        "",
        "| Endpoint Path | Method | Summary |",
        "|---|---|---|"
    ]

    for path, methods in sorted(paths.items()):
        for method, details in methods.items():
            m_str = method.upper()
            summary = details.get("summary", details.get("description", "N/A"))
            surface_lines.append(f"| `{path}` | **{m_str}** | {summary} |")
            
            doc_lines.append(f"### `{m_str}` {path}")
            doc_lines.append(f"**Summary:** {summary}  ")
            if "description" in details and details["description"] != summary:
                doc_lines.append(f"**Description:** {details['description']}  ")
            
            params = details.get("parameters", [])
            if params:
                doc_lines.append("**Parameters:**")
                for p in params:
                    p_name = p.get("name", "")
                    p_in = p.get("in", "")
                    p_req = "required" if p.get("required") else "optional"
                    doc_lines.append(f"- `{p_name}` ({p_in}, {p_req})")
            doc_lines.append("")
            doc_lines.append("---")
            doc_lines.append("")

    DOC_PATH.write_text("\n".join(doc_lines), encoding="utf-8")
    SURFACE_PATH.write_text("\n".join(surface_lines), encoding="utf-8")
    print(f"Synchronized {len(paths)} endpoints across API_DOCUMENTATION.md and API_SURFACE.md")

if __name__ == "__main__":
    sync()
