import logging
import time
import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("chapter22")

app = FastAPI(title="Chapter 22 - Observability")

# ---------------------------------------------------------------------------
# Structured logging with correlation IDs (builds on chapter 8's middleware)
# ---------------------------------------------------------------------------

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f'request_id={request_id} method={request.method} path={request.url.path} '
            f'status={response.status_code} duration_ms={duration_ms:.2f}'
        )
        return response

app.add_middleware(CorrelationIDMiddleware)

# ---------------------------------------------------------------------------
# Metrics: /metrics endpoint in Prometheus text format, auto-instrumented
# for request count, latency histograms, etc across every route.
# ---------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ---------------------------------------------------------------------------
# Dependency health checks -- these simulate real dependency pings.
# ---------------------------------------------------------------------------

class DependencyStatus:
    """Toggle these in tests/demo to simulate a dependency going down."""
    database_up = True
    cache_up = True


def check_database() -> bool:
    return DependencyStatus.database_up


def check_cache() -> bool:
    return DependencyStatus.cache_up


@app.get("/health")
def liveness():
    """
    LIVENESS: "is this process alive and able to respond at all?" Should be
    nearly free to compute and should NOT check downstream dependencies --
    if it does, a downstream outage causes your orchestrator (k8s, etc) to
    think THIS process is dead and restart it, which does nothing to fix the
    actual downstream problem and just adds churn.
    """
    return {"status": "alive"}


@app.get("/ready")
def readiness():
    """
    READINESS: "is this process ready to serve real traffic right now?" DOES
    check dependencies -- if the database is unreachable, this instance
    genuinely can't serve most requests correctly, so a load balancer /
    orchestrator should stop routing traffic to it (without necessarily
    killing/restarting the process, which liveness controls).
    """
    checks = {"database": check_database(), "cache": check_cache()}
    all_ok = all(checks.values())
    status_code = 200 if all_ok else 503
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=status_code, content={"ready": all_ok, "checks": checks})


@app.get("/orders/{order_id}")
def get_order(order_id: int, request: Request):
    logger.info(f"request_id={request.state.request_id} fetching order {order_id}")
    return {"id": order_id, "status": "shipped"}
