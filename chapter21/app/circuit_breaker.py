"""
A minimal circuit breaker, the three-state kind: CLOSED (normal), OPEN
(failing fast, not even trying the real call), HALF_OPEN (cautiously testing
if the dependency has recovered).
"""
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 5.0):
        """
        failure_threshold: consecutive failures before we stop even trying and
                            start failing fast (protects the struggling
                            dependency from more load, and protects OUR
                            latency from being dragged down waiting on it).
        recovery_timeout:   how long to wait in OPEN before allowing one
                            "trial" call through (HALF_OPEN) to check recovery.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at: float | None = None

    def _maybe_transition_to_half_open(self):
        if self.state == CircuitState.OPEN and self.opened_at is not None:
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN

    def call(self, func, *args, **kwargs):
        self._maybe_transition_to_half_open()

        if self.state == CircuitState.OPEN:
            # FAIL FAST: don't even attempt the call. This is the whole point --
            # protect a struggling dependency from more traffic, and protect
            # OUR callers from waiting out a timeout that's very likely to fail
            # anyway.
            raise CircuitOpenError("Circuit is open, failing fast")

        try:
            result = func(*args, **kwargs)
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
            raise
        else:
            # Success (including the HALF_OPEN "trial" call): fully reset.
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            self.opened_at = None
            return result
