# Exercise

Combine `CircuitBreaker` and the `tenacity` retry decorator: wrap calls in a retry that gives up early
(without exhausting all attempts) if the circuit is already open, instead of retrying into a wall.

## Interview-style scenario

Your circuit breaker's `failure_threshold` is 5, `recovery_timeout` is 30s. During a partial outage, the
dependency fails 4 times, recovers briefly, then fails again. Walk through exactly what the breaker's
state does across this sequence, and explain why counting *consecutive* failures (vs. a sliding window)
matters here.
