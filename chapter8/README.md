# Chapter 8 — Middleware

## Concept

Middleware wraps every request/response passing through your app — code that runs before the route
handler (on the way in) and after it (on the way out), regardless of which route matched.

## Why it exists

Some concerns apply to *every* request: logging, CORS headers, compression, a request ID for tracing,
auth token presence checks. Writing that logic into every single route function would be repetitive and
easy to forget on a new endpoint. Middleware puts it in exactly one place.

## Mental model

Middleware nests like parentheses. The **last** middleware you `add_middleware()` runs **first** on the
way in (outermost) and **last** on the way out.

## Diagram

```mermaid
flowchart LR
    Client --> M1[TrustedHost] --> M2[CORS] --> M3[GZip] --> M4[RequestID] --> M5[TimingLogging] --> Route
    Route --> M5b[TimingLogging] --> M4b[RequestID] --> M3b[GZip] --> M2b[CORS] --> M1b[TrustedHost] --> Client
```

## Realistic example

`app/main.py` builds two custom middlewares plus three built-in ones:

- **`RequestIDMiddleware`**: assigns (or honors an incoming) `X-Request-ID`, stores it on
  `request.state`, echoes it in the response header. This is the thread that lets you trace one request
  across your API, a queue consumer, and a downstream service's logs.
- **`TimingLoggingMiddleware`**: logs method, path, status, duration, and the request ID for every
  request — the minimum viable observability you should have from day one (chapter 22 goes further).
- **`CORSMiddleware`**: controls which browser origins may call your API cross-origin.
- **`TrustedHostMiddleware`**: rejects requests with a spoofed `Host` header — mitigates Host header
  injection attacks that some caching/routing setups are vulnerable to.
- **`GZipMiddleware`**: compresses responses over the size threshold.

Run:
```bash
cd chapter8
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
curl -i localhost:8000/ping   # look for X-Request-ID; check the server's console for the timing log line
```

## Common mistakes

- **Order confusion.** Adding auth-checking middleware *after* (i.e., outside) a middleware that logs
  request bodies means the log fires even for requests that will be rejected as unauthenticated — often
  not what you want. Reason explicitly about nesting order, don't guess.
- **`allow_origins=["*"]` with `allow_credentials=True`** — browsers actually forbid this combination
  (`Access-Control-Allow-Origin: *` can't be paired with credentialed requests per the CORS spec), and
  FastAPI/Starlette will reflect it back inconsistently. Be explicit about allowed origins once cookies
  or auth headers are involved.
- **Doing expensive work in middleware that runs on every request**, including ones that will 404 or
  fail auth — middleware runs before routing in some setups, so a heavy "enrich request with user data
  from DB" middleware taxes every request, even ones that don't need it.

## Production considerations

- Correlate the `X-Request-ID` you generate here with the ID your load balancer or API gateway might
  already assign — many teams pass through an upstream-provided ID instead of always generating a new
  one, exactly as `RequestIDMiddleware` does (`request.headers.get("X-Request-ID", <generate>)`).
- `TrustedHostMiddleware` needs your actual production hostnames listed; forgetting to update it after
  adding a new domain is a common self-inflicted outage.

## Exercise

Add an `AuthPresenceMiddleware` that returns 401 immediately for any path under `/admin/*` missing an
`Authorization` header, without touching route code. Then reason about where in the middleware stack it
should sit relative to `TimingLoggingMiddleware` (should a rejected request still be timed/logged?).

## Interview-style scenario

> "Your `TimingLoggingMiddleware` is added, then `RequestIDMiddleware`. A request comes in without an
> `X-Request-ID` header. Walk through, in order, exactly which middleware sees a request ID set on
> `request.state` and which doesn't — and what you'd change in `app.add_middleware()` call order to fix
> it if it's wrong."
