"""Upstream API Circuit Breaker & Resilience Overlay.

Implements a zero-dependency CircuitBreaker state machine (CLOSED, OPEN, HALF_OPEN)
to prevent cascading failures during upstream API latency spikes or outages.
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Zero-dependency circuit breaker for external service call protection."""

    def __init__(
        self,
        name: str = "DefaultCircuitBreaker",
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 30.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def call(self, func: Callable[..., Any], *args, fallback: Optional[Callable[..., Any]] = None, **kwargs) -> Any:
        """Executes func with circuit protection. Runs fallback if OPEN or fails."""
        now = time.time()

        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout_sec:
                logger.info(f"CircuitBreaker '{self.name}' transitioning from OPEN to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
            else:
                logger.warning(f"CircuitBreaker '{self.name}' is OPEN. Executing fallback.")
                if fallback:
                    return fallback(*args, **kwargs)
                return None

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"CircuitBreaker '{self.name}' recovered — resetting to CLOSED.")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = now
            return result
        except Exception as exc:
            self.failure_count += 1
            logger.warning(
                f"CircuitBreaker '{self.name}' recorded failure ({self.failure_count}/{self.failure_threshold}): {exc}"
            )
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                logger.error(f"CircuitBreaker '{self.name}' threshold reached — opening circuit for {self.recovery_timeout_sec}s.")

            if fallback:
                return fallback(*args, **kwargs)
            raise exc
