import os

# Version identifier for the active skill/knowledge library.
# Defaults to the 5‑file system; can be overridden via environment variable.
SKILL_LIBRARY_VERSION: str = os.getenv("SKILL_LIBRARY_VERSION", "5")
