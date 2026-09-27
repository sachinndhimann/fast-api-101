import time
import pytest
from app.circuit_breaker import CircuitBreaker, CircuitState, CircuitOpenError
from app.retry_demo import call_flaky_dependency, TransientError, PermanentError


def test_circuit_opens_after_threshold_failures():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

    def always_fails():
        raise RuntimeError("dependency is down")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(always_fails)
    assert cb.state == CircuitState.OPEN

    # 4th call: circuit is open, fails FAST without even calling always_fails
    with pytest.raises(CircuitOpenError):
        cb.call(always_fails)


def test_circuit_recovers_after_timeout():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.05)

    def always_fails():
        raise RuntimeError("down")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            cb.call(always_fails)
    assert cb.state == CircuitState.OPEN

    time.sleep(0.06)  # wait past recovery_timeout

    def now_succeeds():
        return "recovered"

    result = cb.call(now_succeeds)  # HALF_OPEN trial call succeeds
    assert result == "recovered"
    assert cb.state == CircuitState.CLOSED


def test_retry_succeeds_after_transient_failures():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TransientError("temporary blip")
        return "success"

    result = call_flaky_dependency(flaky)
    assert result == "success"
    assert attempts["count"] == 3


def test_retry_does_not_retry_permanent_errors():
    attempts = {"count": 0}

    def always_permanently_broken():
        attempts["count"] += 1
        raise PermanentError("this will never succeed, e.g. a 404")

    with pytest.raises(PermanentError):
        call_flaky_dependency(always_permanently_broken)
    assert attempts["count"] == 1  # NOT retried -- retry_if_exception_type filtered it out
