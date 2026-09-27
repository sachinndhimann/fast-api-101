# Workflow: Add a new custom middleware

## Problem
You need cross-cutting behavior (e.g. request timing, a custom header check, request/response logging)
applied to every request without editing every route.

## Investigation
Confirm this genuinely needs to run on every/most requests — if it's specific to 2-3 routes, a shared
dependency (chapter 5) is usually a better fit than middleware.

## Implementation
Subclass `BaseHTTPMiddleware` (chapter 8):
```python
class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # before
        response = await call_next(request)
        # after
        return response
app.add_middleware(MyMiddleware)
```
Decide its position relative to existing middleware deliberately — order matters (chapter 8).

## Testing
Test both "middleware runs and does its thing" and "middleware doesn't break routes it shouldn't affect"
— a `TestClient` request to a normal route with assertions on response headers/behavior.

## Validation
Confirm `TrustedHostMiddleware` (if present) allows the test client's host (`testserver`) — a common
false failure in tests unrelated to your new middleware, as chapter 8 shows.

## Production considerations
Measure the latency this middleware adds under load — middleware runs on every request, so even small
per-request overhead compounds at scale.
