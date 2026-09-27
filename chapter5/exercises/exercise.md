# Exercise

Add a `require_role(role: str)` dependency FACTORY (a function returning a dependency), usable as
`Depends(require_role("manager"))`. Contrast with `require_admin`, which hardcodes one role.

## Interview-style scenario

Two dependencies in the same request both depend on `get_settings`. Does FastAPI call it twice? If
`get_settings` weren't cached and just returned a fresh `Settings()` each time, would anything actually
break — or is caching purely a performance optimization here?
