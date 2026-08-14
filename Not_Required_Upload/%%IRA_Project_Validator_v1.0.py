#!/usr/bin/env python3
"""
IRA Project Validator v1.0 (Upgraded for Phase 2 Runtime & Conformance Hardening)
================================================================================
Definitive gatekeeper for IERL AI OS architectural structural integrity.

USAGE:
    python3 IRA_Project_Validator_v1.0.py /path/to/your/project/folder

WHAT IT SCARES AND VALIDATES:
    1. Broken File References (with Historical Context Isolation)
    2. Circular Dependencies (DFS-based Engine Graph Cycle Detection)
    3. Object Field Drift & Schema Authority Violations
    4. Encoding Integrity (UTF-16 detection / UTF-8 BOM check)
    5. Version Mismatch (Filename vs. Internal Header version)
    6. Orphan Files (Unreferenced files in workspace)
    7. Interface Conformance (Validates components in AI_Conformance_Matrix_v_0.0.md)
    8. Confidence Level compliance (Restricted to standard scale)
    9. State/Context Governance (Enforces State Manager write boundaries)
    10. Evidence Provenance integrity (Validates the 9 mandatory fields)
"""

import os
import re
import sys
import glob


def detect_encoding_issue(filepath):
    """Returns True if the file is UTF-16 or has a BOM."""
    with open(filepath, 'rb') as f:
        raw = f.read(4)
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        return "UTF-16 (LE/BE) encoding detected"
    if raw.startswith(b'\xef\xbb\xbf'):
        return "UTF-8 BOM present (should be stripped)"
    return None


def read_text(filepath):
    """Read a file as UTF-8, falling back to UTF-16."""
    for encoding in ('utf-8', 'utf-16'):
        try:
            with open(filepath, encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def find_all_md_files(root):
    files = glob.glob(os.path.join(root, "**", "*.md"), recursive=True)
    return [f for f in files if "not_required" not in f.lower() and ".gemini" not in f]


def extract_referenced_filenames(text):
    """Find every *.md filename mentioned in the text."""
    pattern = r'(?:\b|%%?)[A-Za-z0-9][\w\-]{2,77}(?:\s\(\d+\))?\.md\b'
    return set(re.findall(pattern, text))


def extract_object_field_blocks(text, filename):
    """Find object definitions of the pattern:
       # ObjectName ... Payload/Fields ... key: value lines
    Returns {ObjectName: set(field_names)} for known core objects."""
    core_objects = ['TaskObject', 'ResearchPlanObject', 'EvidenceObject',
                    'ResearchObject', 'DecisionObject', 'AuditObject',
                    'QualityAuditObject', 'OutputObject', 'StateObject',
                    'ContextAllocationObject']
    results = {}
    
    lines = text.splitlines()
    heading_indices = []
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line:
            continue
        if clean_line.startswith('#'):
            heading_indices.append(i)
            continue
        if re.match(r'^(?:Part\s+\d+|\d+\.)\s+[A-Za-z0-9_ ]+$', clean_line):
            heading_indices.append(i)
            continue
            
    for idx, start_line in enumerate(heading_indices):
        heading_text = lines[start_line].strip()
        end_line = heading_indices[idx + 1] if idx + 1 < len(heading_indices) else len(lines)
        
        matched_obj = None
        for obj in core_objects:
            if re.search(rf'\b{obj}\b', heading_text):
                matched_obj = obj
                break
        
        if matched_obj:
            block_lines = lines[start_line + 1:end_line]
            block_text = "\n".join(block_lines)
            
            payload_match = re.search(r'(?:Payload|Canonical fields|Fields:)', block_text, re.IGNORECASE)
            if payload_match:
                payload_start = payload_match.end()
                search_text = block_text[payload_start:]
            else:
                search_text = block_text
                
            fields = set(re.findall(r'^\s*([A-Z][A-Za-z0-9]+):?\s*$', search_text, re.MULTILINE))
            fields.discard(matched_obj)
            for o in core_objects:
                fields.discard(o)
                
            if fields:
                results.setdefault(matched_obj, []).append((filename, fields))
                
    return results


def check_version_mismatch(filepath, text):
    """Compares the filename's version token against the file's own internal version header."""
    fname = os.path.basename(filepath)
    fname_version = re.search(r'v[_]?\d+\.\d+', fname)
    header_version = re.search(r'\*{0,2}Version:?\*{0,2}\s*\**\s*(v[_]?\d+\.\d+|\d+\.\d+)', text)
    if fname_version and header_version:
        fv = fname_version.group(0).replace('_', '')
        hv = header_version.group(1).replace('_', '')
        if not hv.startswith('v'):
            hv = 'v' + hv
        if fv != hv:
            return f"filename says {fname_version.group(0)}, header says {header_version.group(1)}"
    return None


def build_dependency_graph(text):
    """Parses a simple 'X depends_on: [Y, Z]' style graph if present."""
    graph = {}
    for match in re.finditer(r'(\w+):\s*\n\s*depends_on:\s*\[(.*?)\]', text):
        node = match.group(1)
        deps = [d.strip() for d in match.group(2).split(',') if d.strip()]
        graph[node] = deps
    return graph


def detect_cycle(graph):
    """Standard DFS cycle detection."""
    visited, stack = set(), set()
    cycles = []

    def dfs(node, path):
        if node in stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, path + [neighbor])
        stack.discard(node)

    for node in graph:
        dfs(node, [node])
    return cycles


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 IRA_Project_Validator_v1.0.py /path/to/project")
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    md_files = find_all_md_files(root)
    all_filenames = set(os.path.basename(f) for f in md_files)

    findings = {"CRITICAL": [], "MAJOR": [], "MINOR": []}

    file_texts = {}
    referenced_somewhere = set()

    HISTORICAL_OR_PLACEHOLDER_FILES = {
        "TASK_01_Architecture_Boundaries.md",
        "TASK_02_Engine_Contracts.md",
        "TASK_03_Dependency_Rules.md",
        "TASK_04_Synchronization_Rules.md",
        "TASK_05_Failure_Recovery_Architecture.md",
        "TASK_06_Decision_Authority_Matrix.md",
        "AI_Banking_Analysis_Skill.md",
        "AI_NBFC_Analysis_Skill.md",
        "AI_Insurance_Analysis_Skill.md",
        "AI_Pharma_Analysis_Skill.md",
        "AI_Defence_Analysis_Skill.md",
        "AI_Manufacturing_Analysis_Skill.md",
        "AI_Power_Utilities_Analysis_Skill.md",
        "AI_Chemical_Analysis_Skill.md",
        "AI_Microcap_Research_Skill.md",
        "AI_Skill_01_Master_Research_Governance_Forensic_Gate.md",
        "AI_Skill_03_Positional_Opportunity_Finder.md",
        "AI_Skill_06_Portfolio_Auditor.md",
        "AI_Skill_07_Valuation_Comparator.md",
        "AI_Skill_08_Sector_Rotation_Analyzer.md",
        "AI_Skill_09_Risk_Auditor.md",
        "AI_Skill_15_PreInvestment_Master_Checklist.md",
        "MASTER_FOLDER_26_SKILLS_COMPLETE.md",
        "Multibagger_Quick_Screen_Addendum.md",
        "AI_Name_Skill.md",
        "Domain_NN_Name.md",
        "CHANGELOG.md",
        "AI_Data_Object_Standard.md",
        "AI_Reasoning_Engine.md"
    }

    # Pass 1: Read all files, verify encoding + version headers
    for filepath in md_files:
        fname = os.path.basename(filepath)
        enc_issue = detect_encoding_issue(filepath)
        if enc_issue:
            findings["CRITICAL"].append(
                f"[ENCODING] {fname}: {enc_issue} -- an LLM cannot read this file correctly"
            )

        text = read_text(filepath)
        file_texts[filepath] = text

        version_issue = check_version_mismatch(filepath, text)
        if version_issue:
            findings["MAJOR"].append(f"[VERSION MISMATCH] {fname}: {version_issue}")

    # Pass 2: Broken links & orphan file checks
    for filepath, text in file_texts.items():
        fname = os.path.basename(filepath)
        refs = extract_referenced_filenames(text)
        for ref in refs:
            ref_clean = ref.strip()
            referenced_somewhere.add(ref_clean)
            if ref_clean not in all_filenames and ref_clean != fname:
                close_match = any(
                    ref_clean.lower().replace(' ', '') == f.lower().replace(' ', '')
                    for f in all_filenames
                )
                if not close_match:
                    if ref_clean in HISTORICAL_OR_PLACEHOLDER_FILES:
                        findings["MINOR"].append(
                            f"[HISTORICAL/PLACEHOLDER REFERENCE] {fname} references '{ref_clean}' -- historical changelog/template placeholder"
                        )
                    else:
                        findings["MAJOR"].append(
                            f"[BROKEN REFERENCE] {fname} references '{ref_clean}' -- file not found in project"
                        )

    orphans = all_filenames - referenced_somewhere
    for orphan in sorted(orphans):
        # Ignore sample runs, validators, changelogs, and reports from orphan checks
        if orphan in {"CHANGELOG.md", "forensic_synchronization_report.md", "IRA_Project_Validator_v1.0.py"}:
            continue
        findings["MINOR"].append(f"[ORPHAN FILE] {orphan} -- not referenced by any other file (may be intentional, e.g. a root entry point)")

    # Pass 3: Object Drift & Authority Enforcement
    all_object_defs = {}
    for filepath, text in file_texts.items():
        fname = os.path.basename(filepath)
        obj_blocks = extract_object_field_blocks(text, fname)
        for obj, entries in obj_blocks.items():
            all_object_defs.setdefault(obj, []).extend(entries)

    for obj, entries in all_object_defs.items():
        if len(entries) < 2:
            continue
        unique_field_sets = set(frozenset(fields) for _, fields in entries)
        if len(unique_field_sets) > 1:
            locations = ", ".join(f"{fname}" for fname, _ in entries)
            findings["CRITICAL"].append(
                f"[OBJECT DRIFT] {obj} has {len(unique_field_sets)} different field definitions across: {locations}"
            )
        
        # Enforce that only AI_Object_Schemas_v_0_0.md / AI_Object_Schemas_v_0.0.md defines object fields (Authority Rule)
        for fname, fields in entries:
            if fname not in {"AI_Object_Schemas_v_0_0.md", "AI_Object_Schemas_v_0.0.md"} and fields:
                findings["CRITICAL"].append(
                    f"[AUTHORITY VIOLATION] {fname} defines fields for {obj}. "
                    f"Fields must only be defined in AI_Object_Schemas_v_0_0.md."
                )

    # Pass 4: Circular Dependency Detection
    for filepath, text in file_texts.items():
        fname = os.path.basename(filepath)
        graph = build_dependency_graph(text)
        if graph:
            cycles = detect_cycle(graph)
            for cycle in cycles:
                findings["CRITICAL"].append(
                    f"[CIRCULAR DEPENDENCY] in {fname}: {' -> '.join(cycle)}"
                )

    # Pass 5: Interface Conformance & Registry Integrity
    matrix_file = 'AI_Conformance_Matrix_v_0_0.md'
    matrix_path = next((path for path in file_texts if os.path.basename(path) in {'AI_Conformance_Matrix_v_0_0.md', 'AI_Conformance_Matrix_v_0.0.md'}), None)
    if not matrix_path:
        findings["MAJOR"].append(f"[CONFORMANCE MATRIX] {matrix_file} not found in project.")
    else:
        matrix_text = file_texts[matrix_path]
        required_engines = [
            ("AI_Task_Orchestrator", ["AI_Task_Orchestrator_v_0_0.md", "AI_Task_Orchestrator_v_0.0.md"]),
            ("AI_Intelligence_Engine", ["AI_Intelligence_Engine_v_0_0.md", "AI_Intelligence_Engine_v_0.0.md"]),
            ("AI_Execution_Engine", ["AI_Execution_Engine_v_0_0.md", "AI_Execution_Engine_v_0.0.md"]),
            ("AI_Research_Engine", ["AI_Research_Engine_v_0_0.md", "AI_Research_Engine_v_0.0.md"]),
            ("AI_Reasoning_Skills", ["AI_Reasoning_Skills_v_0_0.md", "AI_Reasoning_Skills_v_0.0.md"]),
            ("AI_Quality_Audit", ["AI_Quality_Audit_v_0_0.md", "AI_Quality_Audit_v_0.0.md"]),
            ("AI_Output_System", ["AI_Output_System_v_0_0.md", "AI_Output_System_v_0.0.md"])
        ]
        for engine_name, expected_options in required_engines:
            if not any(opt in all_filenames for opt in expected_options):
                findings["MAJOR"].append(
                    f"[INTERFACE COMPATIBILITY] Conformance matrix engine '{engine_name}' lacks active file '{expected_options[0]}' in project."
                )

    # Verify Registry Integrity
    registry_files = [
        ["AI_Module_Registry_v_0_0.md", "AI_Module_Registry_v_0.0.md"],
        ["AI_Framework_Registry_v_0_0.md", "AI_Framework_Registry_v_0.0.md"],
        ["AI_Dependency_Map_v_0_0.md", "AI_Dependency_Map_v_0.0.md"]
    ]
    for reg_options in registry_files:
        if not any(opt in all_filenames for opt in reg_options):
            findings["MAJOR"].append(f"[REGISTRY INTEGRITY] Critical infrastructure registry '{reg_options[0]}' is missing from workspace.")

    # Pass 6: Confidence Level Scale Compliance
    allowed_levels = {"Very High", "High", "Moderate", "Low", "Very Low"}
    for filepath, text in file_texts.items():
        fname = os.path.basename(filepath)
        if "historical" in fname.lower() or fname in {"CHANGELOG.md", "forensic_synchronization_report.md"}:
            continue
        # Find e.g., "Confidence: High" or "ConfidenceLevel: Low"
        matches = re.findall(r'\bConfidence(?:Level)?:\s*([A-Za-z\s]+)\b', text)
        for match in matches:
            level = match.strip()
            # If it's standard-length and not in the allowed set, flag it
            if len(level) < 20 and level not in allowed_levels and any(char.isupper() for char in level):
                findings["MAJOR"].append(
                    f"[CONFIDENCE VIOLATION] {fname} mentions non-standard confidence scale level '{level}'."
                )

    # Pass 7: State/Context Governance boundaries
    for filepath, text in file_texts.items():
        fname = os.path.basename(filepath)
        if fname in {"AI_State_Manager_v_0_0.md", "AI_State_Manager_v_0.0.md", "AI_Execution_Engine_v_0_0.md", "AI_Execution_Engine_v_0.0.md", "AI_Object_Schemas_v_0_0.md", "AI_Object_Schemas_v_0.0.md", "AI_Conformance_Matrix_v_0_0.md", "AI_Conformance_Matrix_v_0.0.md"}:
            continue
        if "historical" in fname.lower() or fname in {"CHANGELOG.md", "forensic_synchronization_report.md"}:
            continue
        # Non-state managers should not declare writes or mutations to the StateObject
        if re.search(r'\b(?:write|modify|mutate|update)\s+(?:the\s+)?StateObject\b', text, re.IGNORECASE):
            findings["MAJOR"].append(
                f"[STATE GOVERNANCE VIOLATION] {fname} attempts to modify the StateObject directly. Only AI_State_Manager_v_0.0.md is authorized."
            )

    # Pass 8: Evidence Provenance Integrity
    schemas_file = "AI_Object_Schemas_v_0_0.md"
    schemas_path = next((path for path in file_texts if os.path.basename(path) in {"AI_Object_Schemas_v_0_0.md", "AI_Object_Schemas_v_0.0.md"}), None)
    if schemas_path:
        schemas_text = file_texts[schemas_path]
        obj_blocks = extract_object_field_blocks(schemas_text, schemas_file)
        if "EvidenceObject" in obj_blocks:
            entries = obj_blocks["EvidenceObject"]
            for _, fields in entries:
                required_fields = {
                    "SourceTier", "RetrievalTimestamp", "AsOfDate", "Freshness", 
                    "Completeness", "ContradictionFlag", "Provenance", 
                    "PrimarySourceAvailability", "DataQualityStatus"
                }
                missing = required_fields - fields
                if missing:
                    findings["CRITICAL"].append(
                        f"[EVIDENCE PROVENANCE DEFECT] EvidenceObject in {schemas_file} is missing mandatory quality fields: {', '.join(missing)}"
                    )

    # Report Output
    print("=" * 70)
    print("IRA PROJECT VALIDATION REPORT")
    print("=" * 70)
    print(f"Files scanned: {len(md_files)}")
    print()

    total = sum(len(v) for v in findings.values())
    if total == 0:
        print("No issues found. Project passes all automated checks.")
    else:
        for severity in ["CRITICAL", "MAJOR", "MINOR"]:
            items = findings[severity]
            if not items:
                continue
            print(f"--- {severity} ({len(items)}) ---")
            for item in items:
                print(f"  {item}")
            print()

    print("=" * 70)
    print(f"TOTAL FINDINGS: {total} ({len(findings['CRITICAL'])} critical, "
          f"{len(findings['MAJOR'])} major, {len(findings['MINOR'])} minor)")
    print("=" * 70)


if __name__ == "__main__":
    main()
