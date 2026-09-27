import asyncio
import time
import httpx
from fastapi import FastAPI

app = FastAPI(title="Chapter 11 - Async FastAPI")


@app.get("/blocking-in-async")
async def blocking_in_async():
    """
    THE TRAP: `async def` does NOT make blocking code non-blocking. time.sleep()
    blocks the entire event loop -- every other concurrent request on this
    worker process stalls for the full duration, not just this one.
    Hit this endpoint twice concurrently and watch them run SERIALLY.
    """
    time.sleep(1)  # simulates a blocking call: sync DB driver, sync HTTP lib, CPU work
    return {"message": "done (but I blocked everyone else on this worker for 1s)"}


@app.get("/actually-async")
async def actually_async():
    """
    FIXED: asyncio.sleep() yields control back to the event loop, which can
    serve other requests while this one "waits". Hit this endpoint twice
    concurrently and watch them run IN PARALLEL (both finish in ~1s total,
    not ~2s).
    """
    await asyncio.sleep(1)
    return {"message": "done (and I let others run while I waited)"}


@app.get("/blocking-fixed-with-threadpool")
def blocking_fixed_with_threadpool():
    """
    If you MUST call blocking code (a sync library with no async equivalent),
    define the route as a regular `def`, not `async def`. FastAPI automatically
    runs sync route functions in a thread pool, so they don't block the event
    loop -- at the cost of a thread per concurrent request instead of true
    single-threaded concurrency.
    """
    time.sleep(1)
    return {"message": "done (ran in a worker thread, event loop stayed free)"}


@app.get("/aggregate")
async def aggregate_apis():
    """
    Concurrent API aggregation: fetch multiple independent things in parallel
    with asyncio.gather instead of one after another. 3 calls at ~200ms each
    finish in ~200ms total here instead of ~600ms sequentially.
    """
    async with httpx.AsyncClient() as client:
        urls = [
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
            "https://httpbin.org/delay/0",
        ]
        start = time.perf_counter()
        responses = await asyncio.gather(*(client.get(u, timeout=5) for u in urls))
        elapsed = time.perf_counter() - start
    return {"count": len(responses), "elapsed_seconds": round(elapsed, 2)}


@app.get("/background-task-demo")
async def background_task_demo():
    """See chapter 16 for the full BackgroundTasks vs Celery vs queue comparison."""
    return {"message": "for fire-and-forget work, see FastAPI's BackgroundTasks (chapter 16)"}
