"""Phase 3 Security: Adversarial Prompt Injection Defense & Sanitizer Module.

Protects Generative AI services (Red-Team Bot, Concall NLP, AI Committee) from:
- Indirect prompt injection attacks
- Instruction hijacking and system prompt override attempts
- Hidden delimiter / payload injection
- System role impersonation
"""

import re
import logging
import unicodedata
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


# Known prompt injection attack signatures (case-insensitive regex patterns)
INJECTION_SIGNATURES: List[Tuple[str, str]] = [
    (r"(?i)ignore\s+(all\s+)?(previous|above|prior|system|future)?\s*instructions?", "INSTRUCTION_OVERRIDE"),
    (r"(?i)disregard\s+(all\s+)?(previous|prior|system|future)?\s*(prompts?|rules?|directives?|instructions?)", "DISREGARD_DIRECTIVE"),
    (r"(?i)(set\s+aside|forget)\s+(all\s+)?(previous|prior|system|given)?\s*(guidance|rules?|instructions?|prompts?)", "INSTRUCTION_OVERRIDE"),
    (r"(?i)system\s*:\s*you\s+are", "ROLE_IMPERSONATION"),
    (r"(?i)act\s+as\s+a\s+(dan|jailbroken|unrestricted)\s+ai", "JAILBREAK_ATTEMPT"),
    (r"(?i)forget\s+everything\s+you\s+were\s+told", "CONTEXT_WIPE"),
    (r"(?i)override\s+security\s+protocols?", "SECURITY_OVERRIDE"),
    (r"(?i)print\s+(the\s+)?(system\s+prompt|api\s*key|secret\s*token)", "SECRET_EXFILTRATION"),
    (r"(?i)<\s*system\s*>", "SYSTEM_TAG_INJECTION"),
    (r"(?i)```\s*system", "MARKDOWN_SYSTEM_INJECTION"),
    (r"(?i)\[\s*system\s*note\s*:", "BRACKET_SYSTEM_INJECTION"),
]


def sanitize_prompt(text: str, max_length: int = 4096) -> Dict[str, Any]:
    """Sanitizes user-provided text inputs against prompt injection payloads.

    Args:
        text: Raw input string (thesis, transcript snippet, natural language query).
        max_length: Maximum allowed character length for prompt inputs.

    Returns:
        Dict containing:
        - is_safe (bool): True if input contains no injection threats.
        - sanitized_text (str): Neutralized and truncated prompt text.
        - detected_threats (List[str]): List of detected attack signature tags.
        - original_length (int): Length of input before sanitization.
    """
    if not text:
        return {
            "is_safe": True,
            "sanitized_text": "",
            "detected_threats": [],
            "original_length": 0
        }

    # Normalize Unicode homoglyphs and strip zero-width/control characters
    raw_input = str(text).strip()
    normalized_input = unicodedata.normalize("NFKD", raw_input)
    normalized_input = "".join(c for c in normalized_input if not unicodedata.category(c).startswith("C"))
    detected_threats = []

    # Check for known attack signatures
    for pattern, threat_tag in INJECTION_SIGNATURES:
        if re.search(pattern, normalized_input):
            detected_threats.append(threat_tag)

    # Neutralize threat patterns by replacing suspicious instruction phrases
    cleaned = raw_input
    for pattern, _ in INJECTION_SIGNATURES:
        cleaned = re.sub(pattern, "[REDACTED_PROMPT_INJECTION]", cleaned)

    # Strip dangerous HTML/XML tag structures
    cleaned = re.sub(r"<\s*/?\s*(script|system|prompt|instruction|role)\b[^>]*>", "[REDACTED_TAG]", cleaned, flags=re.IGNORECASE)

    # Enforce maximum safe character length truncation
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "... [TRUNCATED]"

    is_safe = len(detected_threats) == 0

    if not is_safe:
        logger.warning(
            "PROMPT INJECTION ATTEMPT NEUTRALIZED: Threats=%s OriginalLength=%d",
            detected_threats, len(raw_input)
        )

    return {
        "is_safe": is_safe,
        "sanitized_text": cleaned,
        "detected_threats": detected_threats,
        "original_length": len(raw_input)
    }
