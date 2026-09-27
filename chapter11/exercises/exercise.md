# Exercise

Add `/mixed`: one truly-async op (`asyncio.sleep`) plus one CPU-bound op (a large Fibonacci computed
synchronously) in the same request. Predict, then measure, behavior under 5 concurrent requests, and
explain why `asyncio.gather` doesn't help the CPU-bound half.

## Interview-style scenario

A team migrates Flask to FastAPI, marking every route `async def` without touching the underlying
`psycopg2` calls, expecting a free win. Load testing shows P99 latency got *worse* under concurrency.
Explain precisely why.
