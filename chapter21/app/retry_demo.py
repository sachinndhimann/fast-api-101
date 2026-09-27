"""
Retry with exponential backoff, using tenacity. This is what you'd wrap
around a call to a flaky downstream dependency (chapter 18's inter-service
HTTP calls are a prime candidate).
"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class TransientError(Exception):
    """Represents a retryable failure -- a timeout, a 503, a connection reset."""


class PermanentError(Exception):
    """Represents a non-retryable failure -- a 400, a 404. Retrying won't help."""


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=0.01, max=1),  # small multiplier so tests run fast; use seconds in prod
    retry=retry_if_exception_type(TransientError),   # ONLY retry transient errors, never permanent ones
    reraise=True,
)
def call_flaky_dependency(fn):
    """fn is called with no args and should raise TransientError/PermanentError or return a value."""
    return fn()
