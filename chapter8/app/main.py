import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("chapter8")

app = FastAPI(title="Chapter 8 - Middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware: assigns a correlation ID to every request, echoes it
    back in the response, and makes it available to route handlers via
    request.state. This ID is what lets you grep logs across every layer
    (this API, a downstream service, a queue consumer) for ONE request.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status, duration and the request ID for every request."""
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", "-")
        logger.info(
            f'request_id={request_id} method={request.method} path={request.url.path} '
            f'status={response.status_code} duration_ms={duration_ms:.2f}'
        )
        return response


# ---------------------------------------------------------------------------
# ORDER MATTERS. Middleware added LAST runs FIRST on the way in, and LAST on
# the way out (it wraps everything added before it) -- like nested parentheses.
# Here: TrustedHost -> CORS -> GZip -> RequestID -> TimingLogging -> route
# and back out in reverse.
# ---------------------------------------------------------------------------
app.add_middleware(TimingLoggingMiddleware)   # innermost of our custom pair: sees the ID already set
app.add_middleware(RequestIDMiddleware)       # outer of our custom pair: sets the ID first
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],   # never "*" once you also allow_credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com", "testserver"],  # "testserver" is what FastAPI's TestClient sends
)


@app.get("/ping")
def ping(request: Request):
    return {"message": "pong", "request_id": request.state.request_id}


@app.get("/slow")
async def slow():
    import asyncio
    await asyncio.sleep(0.2)
    return {"message": "that took a while, check the timing log"}
