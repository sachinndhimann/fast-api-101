# Exercise

Take chapter 10's rate limiter test suite and rerun it, swapping the shared Redis client for two
separate in-memory dicts (one per "instance," like `StatefulInstance`). Show precisely how the effective
rate limit becomes 2x looser than configured with 2 instances instead of 1.

## Interview-style scenario

Your API runs as a single instance today and works fine. Ops wants to scale to 4 instances ahead of a
traffic spike. What's your checklist to verify before that scale-up, based on this chapter?
