"""Safe Data Extractor Utility — Zero-Trust Data Extraction.

Provides safe numeric and ratio extraction without synthetic silent defaults.
Enforces the Absence-of-Evidence law: missing data returns None,
never a synthetic favorable default.
"""

from typing import Any, Dict, Optional


class SafeDataExtractor:
    """Safe data extraction routines that prevent silent null coercions."""

    @staticmethod
    def get_numeric(
        data: Optional[Dict[str, Any]],
        key: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> Optional[float]:
        """Extract a numeric float from dict if present and within valid range."""
        if not data or not isinstance(data, dict):
            return None
        val = data.get(key)
        if val is None or val == "":
            return None
        try:
            f_val = float(val)
            if min_val is not None and f_val < min_val:
                return None
            if max_val is not None and f_val > max_val:
                return None
            return f_val
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_percentage(
        data: Optional[Dict[str, Any]],
        key: str,
        allow_zero: bool = True,
    ) -> Optional[float]:
        """Extract a percentage ratio [0.0, 100.0] without defaulting None to 0.0."""
        return SafeDataExtractor.get_numeric(data, key, min_val=0.0 if allow_zero else 0.0001, max_val=100.0)
