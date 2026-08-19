"""Build auditable Claude Project upload bundles from the canonical source files.

The source files remain the source of truth.  This compiler only adds an
operating wrapper and never trims or rewrites a source payload.
"""

import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "canonical_source"
COMPILER_VERSION = "2.0"
PROJECT_VERSION = "0.4.0"
SCHEMA_VERSION = "1.0"


def get_git_commit() -> str:
    try:
        res = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL)
        return res.decode("utf-8").strip()
    except Exception:
        return "UNKNOWN"


def compute_source_hash() -> str:
    hasher = hashlib.sha256()
    if not SOURCE_DIR.exists():
        return "UNKNOWN"
    for filepath in sorted(SOURCE_DIR.rglob("*")):
        if filepath.is_file():
            try:
                hasher.update(filepath.read_bytes())
            except Exception:
                pass
    return hasher.hexdigest()


FIVE_FILE_MAP = {
    "01_Master_System_Core_Instructions_Architecture.md": [
        "AI_Project_Instructions_v_0_0.md", "AI_Architecture_Overview_v_0_0.md",
        "AI_Pipeline_Specification_v_0_0.md", "AI_Task_Orchestrator_v_0_0.md",
        "AI_State_Manager_v_0_0.md", "AI_Context_Manager_v_0_0.md",
        "AI_Confidence_Standard_v_0_0.md", "AI_Explainability_Standard_v_0_0.md",
    ],
    "02_Master_Engine_Contracts_Schemas_Registries.md": [
        "AI_Intelligence_Engine_v_0_0.md", "AI_Execution_Engine_v_0_0.md",
        "AI_Research_Engine_v_0_0.md", "AI_Reasoning_Skills_v_0_0.md",
        "AI_Quality_Audit_v_0_0.md", "AI_Output_System_v_0_0.md",
        "AI_Object_Schemas_v_0_0.md", "AI_Dependency_Map_v_0_0.md",
        "AI_Unified_Pattern_Taxonomy_v_0_0.md", "AI_Module_Registry_v_0_0.md",
        "AI_Framework_Registry_v_0_0.md", "AI_Conformance_Matrix_v_0_0.md",
        "AI_E6_Quality_Growth_Screener_v_0_0.md", "AI_Causal_Analysis_Engine_v_0_0.md",
        "AI_Geopolitical_Risk_Engine_v_0_0.md",
    ],
    "03_Master_Skill_Library.md": [
        "AI_SKILL_IRA_col_final/04_Skills_Reference_v_0_0.md",
        "AI_SKILL_IRA_col_final/AI_18_Expert_Strategies_Execution_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Comparison_Engine_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Concentrated_SmallCap_Style_Thinking_Skill.md",
        "AI_SKILL_IRA_col_final/AI_DCF_Valuation_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Forensic_Accounting_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Fundamental_Analysis_Core_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Future_Growth_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Multibagger_Discovery_Skill.md",
        "AI_SKILL_IRA_col_final/AI_MultiSector_Momentum_Value_Style_Thinking_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Options_Data_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Portfolio_Construction_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Small_to_Mid_Cap_SIP_Stocks_Analysis_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Swing_Trading_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Technical_Analysis_Master_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Turnaround_Analysis_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Uptrend_Momentum_Stock_Skill.md",
        "AI_SKILL_IRA_col_final/AI_Volume_Delivery_Analysis_Skill.md",
    ],
    "04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md": [
        "Knowledge_IRA_COL_FINAL/00_Index.md", "Knowledge_IRA_COL_FINAL/Domain_01_Economics.md",
        "Knowledge_IRA_COL_FINAL/Domain_02_Financial_Statements.md", "Knowledge_IRA_COL_FINAL/Domain_03_Accounting.md",
        "Knowledge_IRA_COL_FINAL/Domain_04_Financial_Ratios.md", "Knowledge_IRA_COL_FINAL/Domain_05_Valuation.md",
        "Knowledge_IRA_COL_FINAL/Domain_06_Fundamental_Analysis.md", "Knowledge_IRA_COL_FINAL/Domain_07_Technical_Analysis.md",
        "Knowledge_IRA_COL_FINAL/Domain_08_Corporate_Governance.md", "Knowledge_IRA_COL_FINAL/Domain_09_Risk_Management.md",
        "Knowledge_IRA_COL_FINAL/Domain_10_Portfolio_Management.md", "Knowledge_IRA_COL_FINAL/Domain_11_Behavioural_Finance.md",
        "Knowledge_IRA_COL_FINAL/Domain_12_Industry_Knowledge.md", "Knowledge_IRA_COL_FINAL/Domain_13_Macroeconomic_Themes.md",
        "Knowledge_IRA_COL_FINAL/Domain_14_Indian_Capital_Markets.md", "Knowledge_IRA_COL_FINAL/Domain_15_Investor_Frameworks.md",
        "Knowledge_IRA_COL_FINAL/Domain_16_Special_Situations.md", "Knowledge_IRA_COL_FINAL/Domain_17_Research_Sources.md",
        "Knowledge_IRA_COL_FINAL/Domain_18_ESG_Sustainability.md", "Knowledge_IRA_COL_FINAL/Domain_19_Derivatives_Options.md",
        "Knowledge_IRA_COL_FINAL/Domain_20_Credit_Debt_Markets.md", "Knowledge_IRA_COL_FINAL/Domain_21_Quantitative_Factor_Models.md",
        "Knowledge_IRA_COL_FINAL/Domain_22_Regulatory_Tax_Framework.md", "Knowledge_IRA_COL_FINAL/Domain_23_MA_Deal_Analysis.md",
    ],
    "05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md": [
        "Knowledge_IRA_COL_FINAL/Domain_24_Forensic_Accounting.md", "Knowledge_IRA_COL_FINAL/Domain_25_Moat_Competitive_Advantage.md",
        "Knowledge_IRA_COL_FINAL/Domain_26_Financial_Institution_Analysis.md", "Knowledge_IRA_COL_FINAL/Domain_27_Super_Investor_Tracking.md",
        "Knowledge_IRA_COL_FINAL/Domain_28_Multibagger_Turnaround_Framework.md", "Knowledge_IRA_COL_FINAL/Domain_29_MicroCap_Risk_Framework.md",
        "Knowledge_IRA_COL_FINAL/Domain_30_Swing_Positional_Technical_Patterns.md", "Knowledge_IRA_COL_FINAL/Domain_31_Banking_Sector_DeepDive.md",
        "Knowledge_IRA_COL_FINAL/Domain_32_Pharma_Sector_DeepDive.md", "Knowledge_IRA_COL_FINAL/Domain_33_Defence_Sector_DeepDive.md",
        "Knowledge_IRA_COL_FINAL/Domain_34_Manufacturing_Sector_DeepDive.md", "Knowledge_IRA_COL_FINAL/Domain_35_REIT_InvIT_Sector_DeepDive.md",
        "Knowledge_IRA_COL_FINAL/Domain_36_Insurance_Sector_DeepDive.md", "Knowledge_IRA_COL_FINAL/Domain_37_Logistics_Sector_DeepDive.md",
        "Knowledge_IRA_COL_FINAL/Domain_38_Power_Sector_DeepDive.md", "Knowledge_IRA_COL_FINAL/Domain_39_Railways_Sector_DeepDive.md",
        "Knowledge_IRA_COL_FINAL/Domain_40_Screening_Strategies.md", "Knowledge_IRA_COL_FINAL/Domain_41_Dividend_Analysis.md",
        "Knowledge_IRA_COL_FINAL/Domain_42_Scuttlebutt_Research.md", "Knowledge_IRA_COL_FINAL/Domain_43_Portfolio_Management_Rules.md",
        "Knowledge_IRA_COL_FINAL/Domain_44_Geo_Economic_Impact.md",
        "Knowledge_IRA_COL_FINAL/Domain_45_Rule_Based_Options_Systematic_Strategies.md",
        "Knowledge_IRA_COL_FINAL/Domain_46_Technical_Growth_Second_Brain_Strategies.md",
        "Knowledge_IRA_COL_FINAL/Domain_47_Fundamental_Value_Structural_Strategies.md",
        "Knowledge_IRA_COL_FINAL/Domain_48_Quant_Momentum_Ethical_Screening_Strategies.md",
        "Knowledge_IRA_COL_FINAL/Screener_Field_Glossary_v_0_0.md",
        "Knowledge_IRA_COL_FINAL/Sector_Quick_Reference_v_0_0.md",
    ],

}

NINE_FILE_MAP = {
    "01_System_Core_Instructions_Architecture.md": FIVE_FILE_MAP["01_Master_System_Core_Instructions_Architecture.md"],
    "02_Engine_Contracts_Schemas_Registries.md": FIVE_FILE_MAP["02_Master_Engine_Contracts_Schemas_Registries.md"],
    "03_Workflow_Skills_01_to_25.md": ["AI_SKILL_IRA_col_final/04_Skills_Reference_v_0_0.md"],
    "04_Analytical_Lens_Skills_26_to_41.md": FIVE_FILE_MAP["03_Master_Skill_Library.md"][1:],
    "05_Knowledge_Base_Vol_1_Economics_Financials.md": FIVE_FILE_MAP["04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md"][:12],
    "06_Knowledge_Base_Vol_2_Markets_Governance_Macro.md": FIVE_FILE_MAP["04_Master_Knowledge_Base_Vol_1_Fundamentals_Valuation_Governance.md"][12:],
    "07_Knowledge_Base_Vol_3_Forensics_Moats_Banking.md": FIVE_FILE_MAP["05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md"][:8],
    "08_Knowledge_Base_Vol_4_Sector_Deep_Dives.md": FIVE_FILE_MAP["05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md"][8:17],
    "09_Knowledge_Base_Vol_5_Screening_Portfolio_Glossaries.md": FIVE_FILE_MAP["05_Master_Knowledge_Base_Vol_2_Sectors_Frameworks_Screening.md"][17:],
}

EXCLUDED_PRIVATE_OR_INTEGRATION_FILES = {
    "API_KEYS_CONFIG.env", ".env.example", "API_PROVIDERS_AND_FREE_TIERS_GUIDE.md", "test_apis.py",
}


def label(path: str) -> str:
    return Path(path).stem.replace("_v_0_0", "").replace("_", " ")


def source_record(rel_file: str) -> tuple[str, str, int]:
    payload = (SOURCE_DIR / rel_file).read_text(encoding="utf-8")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return payload, digest, len(payload.encode("utf-8"))


def bundle_navigation(mapping: dict) -> str:
    rows = ["| Upload file | Primary use | Sources |", "|---|---|---:|"]
    for filename, files in mapping.items():
        role = label(filename).replace("Master ", "")
        rows.append(f"| `{filename}` | {role} | {len(files)} |")
    return "\n".join(rows)


def operating_wrapper(master_filename: str, files: list[str], mapping: dict, manifest_meta: dict) -> str:
    manifest = []
    for position, rel_file in enumerate(files, 1):
        _, digest, byte_count = source_record(rel_file)
        manifest.append(f"| {position} | `{Path(rel_file).name}` | {byte_count:,} | `{digest}` |")
    return f"""# {Path(master_filename).stem}

> **IERL AI Equity OS — curated upload artifact**  
> Project Version: `{manifest_meta['PROJECT_VERSION']}` · Bundle Version: `{manifest_meta['BUNDLE_VERSION']}` · Source Commit: `{manifest_meta['GIT_COMMIT_SOURCE']}`  
> Generated At: `{manifest_meta['GENERATED_AT']}` · Source Hash: `{manifest_meta['SOURCE_HASH'][:16]}` · Compiler: `consolidate_project.py` v{COMPILER_VERSION}

## Operating contract

This is a generated, read-only working volume. The separately maintained source documents are authoritative; regenerate this file after changing a source. The wrapper provides navigation and execution discipline, but does not replace a source rule. Embedded source payloads are preserved verbatim between the `BEGIN` and `END` markers.

1. Route the request to the narrowest relevant upload file, then use the named embedded document(s); do not treat an unrelated volume as evidence.
2. Execute applicable skill steps in order. If a required input, timeframe, benchmark, or source is absent, state the gap and the effect on confidence; never silently invent it.
3. Separate **reported facts**, **calculations**, **assumptions**, and **inference**. Date all market-sensitive claims and identify the data source or user-provided input.
4. Surface disconfirming evidence, governance/forensic risk, liquidity risk, valuation risk, and material uncertainty before a conclusion. A positive screen is not investment advice or a guarantee.
5. When source documents conflict, prefer the more specific, later-versioned requirement; if unresolved, disclose the conflict and use the more conservative interpretation. Never override platform safety requirements.

## Fast task routing

{bundle_navigation(mapping)}

**Default research sequence:** define decision and horizon → gather dated evidence → run the relevant workflow/analytical skill → apply risk and forensic checks → calculate/compare → present conclusion, counter-case, and confidence. For a company decision, consult core instructions, the applicable skill, fundamentals/valuation, sector context, and risk/forensics rather than relying on one metric.

## Scope and privacy boundary

This bundle contains static methodology and knowledge only. It contains no credentials and cannot by itself read local files, call APIs, fetch live market data, trade, or access private accounts. The following local integration/private files are intentionally excluded: {", ".join(f"`{name}`" for name in sorted(EXCLUDED_PRIVATE_OR_INTEGRATION_FILES))}.

## Embedded source manifest

The SHA-256 values cover the exact UTF-8 source payload, not this wrapper. Use the manifest to audit a rebuild.

| # | Source document | UTF-8 bytes | SHA-256 |
|---:|---|---:|---|
{chr(10).join(manifest)}

---

"""


def build_master_files(mapping: dict, target_dir: Path, manifest_meta: dict) -> None:
    target_dir.mkdir(exist_ok=True)
    bundle_manifest = {
        "manifest_metadata": manifest_meta,
        "bundle_files": {}
    }
    
    for master_filename, file_list in mapping.items():
        missing = [item for item in file_list if not (SOURCE_DIR / item).is_file()]
        if missing:
            raise FileNotFoundError(f"Cannot build {master_filename}; missing: {missing}")
        if any(Path(item).name in EXCLUDED_PRIVATE_OR_INTEGRATION_FILES for item in file_list):
            raise ValueError(f"Private/integration file included in {master_filename}")

        chunks = [operating_wrapper(master_filename, file_list, mapping, manifest_meta)]
        file_sources = []
        for position, rel_file in enumerate(file_list, 1):
            payload, digest, byte_count = source_record(rel_file)
            chunks.append(f"<!-- BEGIN SYSTEM FILE {position}: {Path(rel_file).name} | SHA256: {digest} -->\n")
            chunks.append(f"## Embedded source {position}: {label(rel_file)}\n\n")
            chunks.append(payload)
            if not payload.endswith("\n"):
                chunks.append("\n")
            chunks.append(f"<!-- END SYSTEM FILE {position}: {Path(rel_file).name} -->\n\n---\n\n")
            source_path = f"canonical_source/{rel_file}".replace("\\", "/")
            file_sources.append({
                "position": position,
                "source": rel_file,
                "source_path": source_path,
                "sha256": digest,
                "bytes": byte_count
            })

        output = "".join(chunks)
        (target_dir / master_filename).write_text(output, encoding="utf-8", newline="")
        bundle_manifest["bundle_files"][master_filename] = {
            "sources_count": len(file_list),
            "output_bytes": len(output.encode("utf-8")),
            "sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
            "embedded_sources": file_sources
        }
        print(f"Created: {master_filename} ({len(file_list)} source files; {len(output.encode('utf-8')):,} bytes)")

    # Stamp companion MANIFEST.json in bundle directory
    (target_dir / "MANIFEST.json").write_text(json.dumps(bundle_manifest, indent=2), encoding="utf-8", newline="")
    print(f"Stamped: {target_dir.name}/MANIFEST.json")


def validate(mapping: dict, target_dir: Path) -> None:
    expected = [Path(path).name for files in mapping.values() for path in files]
    if len(expected) != len(set(expected)):
        raise ValueError("A source document appears more than once in this bundle")
    for filename, files in mapping.items():
        output = (target_dir / filename).read_text(encoding="utf-8")
        actual = output.count("<!-- BEGIN SYSTEM FILE ")
        if actual != len(files):
            raise ValueError(f"{filename}: expected {len(files)} source markers, found {actual}")
    print(f"Validated: {target_dir.name} — {len(expected)} unique embedded sources")


def main() -> None:
    git_commit_source = get_git_commit()
    source_hash = compute_source_hash()
    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    manifest_meta = {
        "PROJECT_VERSION": PROJECT_VERSION,
        "BUNDLE_VERSION": "2.0",
        "SCHEMA_VERSION": SCHEMA_VERSION,
        "GIT_COMMIT_SOURCE": git_commit_source,
        "GIT_COMMIT": git_commit_source,
        "GENERATED_AT": generated_at,
        "GENERATOR_VERSION": COMPILER_VERSION,
        "SOURCE_HASH": source_hash
    }

    targets = (
        (FIVE_FILE_MAP, BASE_DIR / "CONSOLIDATED_5_FILE_SYSTEM"),
        (NINE_FILE_MAP, BASE_DIR / "CONSOLIDATED_9_FILE_SYSTEM")
    )
    for mapping, target in targets:
        build_master_files(mapping, target, manifest_meta)
        validate(mapping, target)


if __name__ == "__main__":
    main()

