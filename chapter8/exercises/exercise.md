# Exercise

Add an `AuthPresenceMiddleware` that 401s any `/admin/*` path missing an `Authorization` header, without
touching route code. Decide where it should sit relative to `TimingLoggingMiddleware` — should a
rejected request still be timed and logged?

## Interview-style scenario

`TimingLoggingMiddleware` is added first, then `RequestIDMiddleware`. A request arrives with no
`X-Request-ID` header. Trace which middleware sees a request ID on `request.state` and which doesn't —
and what `add_middleware()` order change would fix it if it's wrong.
