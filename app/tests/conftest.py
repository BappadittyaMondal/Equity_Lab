"""Pytest shared test fixtures and environment configuration.
"""

import pytest
import os
from app.core.security import rate_limiter

os.environ["OFFLINE_TEST_MODE"] = "true"


@pytest.fixture(autouse=True)
def reset_rate_limiter_state():
    """Resets rate limiter memory before every single test to guarantee test isolation."""
    rate_limiter.reset()
    yield
    rate_limiter.reset()
