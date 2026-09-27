"""
Demonstrates WHY statelessness matters for horizontal scaling: an in-memory
counter breaks the moment you have more than one instance, because each
instance has its OWN memory. A Redis-backed counter works identically
regardless of how many instances exist, because state lives outside any one
process.
"""
import fakeredis  # stand-in for real Redis in this demo/tests


class StatefulInstance:
    """BAD: state lives in process memory. Instance A's counter and instance B's
    counter are independent -- a load balancer routing requests between them
    means the counter value depends on WHICH instance happened to serve you."""
    def __init__(self):
        self.counter = 0

    def increment(self) -> int:
        self.counter += 1
        return self.counter


class StatelessInstance:
    """GOOD: state lives in Redis, shared by every instance. It doesn't matter
    which instance serves a given request -- the counter is consistent."""
    def __init__(self, redis_client):
        self.redis = redis_client

    def increment(self) -> int:
        return self.redis.incr("shared_counter")
