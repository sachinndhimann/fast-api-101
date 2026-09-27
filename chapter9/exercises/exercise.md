# Exercise

Add `RateLimitedError` (429) to the hierarchy plus a route that raises it. Add a `retry_after` field to
the error envelope, but only for this error type, without breaking `error_envelope()`'s shared contract.

## Interview-style scenario

A client team says your API "sometimes returns HTML instead of JSON on errors." What FastAPI/Starlette
behavior causes that, and where would you look first?
