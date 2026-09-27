# Workflow: Add JWT authentication to an existing service

## Problem
Your API currently has no auth, and you need to add login + protected routes without breaking existing
unauthenticated endpoints that should stay public (e.g. `/health`).

## Investigation
List every existing route and classify: must be protected, must stay public, or is ambiguous (needs a
product decision, not an engineering one).

## Implementation
Follow chapter 6 exactly: add `app/security.py` (hashing + JWT encode/decode), `app/deps.py`
(`get_current_user` via `OAuth2PasswordBearer`), and `/auth/register`, `/auth/login`, `/auth/refresh`
routes. Then add `Depends(get_current_user)` to every route that should require auth — FastAPI won't do
this automatically; it's opt-in per route.

## Testing
Write tests for: successful login, wrong password (401), accessing a protected route with no token
(401), with an expired token (401), with a valid token (200). See chapter 6's `test_auth.py`.

## Validation
Confirm previously-public routes (`/health`) still work with NO token, and previously-open routes that
should now be protected correctly reject unauthenticated requests — a common regression is protecting
too much (breaking health checks) or too little (leaving a sensitive route open).

## Production considerations
Rotate `JWT_SECRET_KEY` out of any default/example value before deploying — chapter 6's dev secret is
deliberately obvious so it's never mistaken for production-ready.
