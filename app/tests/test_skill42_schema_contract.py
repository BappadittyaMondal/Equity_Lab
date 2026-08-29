"""Automated Contract Test: Skill 42 Markdown Output Format vs GenAIRedTeamService Schema."""

import json
import re
from pathlib import Path
from app.services.research.genai_redteam_service import GenAIRedTeamService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_skill42_schema_contract_parity():
    """Assert that Skill 42 Markdown ## Output Format JSON keys match GenAIRedTeamService field-for-field."""
    skill_file = PROJECT_ROOT / "canonical_source" / "AI_SKILL_IRA_col_final" / "AI_Four_Lens_Evidence_Weighting_Skill.md"
    assert skill_file.exists(), f"Skill 42 canonical file missing at {skill_file}"

    content = skill_file.read_text(encoding="utf-8")
    
    # Extract JSON block under Output Format
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    assert json_match is not None, "Failed to locate ```json block under Output Format in Skill 42"

    markdown_schema = json.loads(json_match.group(1))
    markdown_keys = set(markdown_schema.keys())

    # Get runtime synthesized output keys from GenAIRedTeamService
    runtime_output = GenAIRedTeamService.synthesize_four_lens_evidence("RELIANCE")
    runtime_keys = set(runtime_output.keys()) - {"symbol"}  # symbol is standard runtime context

    # Assert exact key parity
    assert markdown_keys == runtime_keys, (
        f"Schema Contract Mismatch! Markdown keys {markdown_keys} != Runtime keys {runtime_keys}"
    )

    # Assert nested evidence structure
    for lens in ["kacholia_evidence", "kedia_evidence", "agrawal_evidence", "parikh_evidence"]:
        assert lens in runtime_output
        assert "finding" in runtime_output[lens]
        assert "evidence_quality" in runtime_output[lens]
        assert runtime_output[lens]["evidence_quality"] in ["HIGH", "MEDIUM", "LOW"]
