import fakeredis
from app.stateless_demo import StatefulInstance, StatelessInstance

def test_stateful_instances_diverge_under_load_balancing():
    a, b = StatefulInstance(), StatefulInstance()
    results = [(a if i % 2 == 0 else b).increment() for i in range(4)]
    assert results == [1, 1, 2, 2]  # each instance only knows about its own half of the traffic

def test_stateless_instances_stay_consistent_under_load_balancing():
    redis = fakeredis.FakeStrictRedis()
    a, b = StatelessInstance(redis), StatelessInstance(redis)
    results = [(a if i % 2 == 0 else b).increment() for i in range(4)]
    assert results == [1, 2, 3, 4]  # consistent regardless of which instance served the request
