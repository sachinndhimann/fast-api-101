import asyncio
import signal
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chapter25")

IN_FLIGHT_REQUESTS = {"count": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown hooks. Use this to open a DB connection pool on startup
    and close it cleanly on shutdown -- resources acquired here are guaranteed
    to be released even on a clean SIGTERM shutdown (see graceful shutdown below).
    """
    logger.info("Starting up: opening connection pools, warming caches, etc.")
    yield
    logger.info("Shutting down: closing connection pools cleanly.")


app = FastAPI(title="Chapter 25 - Production Deployment", lifespan=lifespan)


@app.middleware("http")
async def track_in_flight(request, call_next):
    IN_FLIGHT_REQUESTS["count"] += 1
    try:
        return await call_next(request)
    finally:
        IN_FLIGHT_REQUESTS["count"] -= 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"ready": True}


@app.get("/slow")
async def slow():
    """Simulates a request in flight during a deploy -- used to demo graceful shutdown."""
    await asyncio.sleep(3)
    return {"message": "finished despite a shutdown signal arriving mid-request"}
