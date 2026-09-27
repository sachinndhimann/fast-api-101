# Exercise

Extend `lifespan` to open a real async SQLAlchemy engine (chapter 4) on startup and dispose it on
shutdown, storing it on `app.state`. Confirm via logging that disposal happens exactly once.

## Interview-style scenario

During a deploy, you see a 10-second spike of 502s from your load balancer each time. Readiness probes
are configured correctly. What's the most likely remaining cause, and how does Gunicorn's
`--graceful-timeout` relate to fixing it?
