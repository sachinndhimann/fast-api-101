"""
Standalone Orders service. Talks to the Users service over HTTP -- this is
the fundamental shift from chapter 17: a Python function call became a
network call, with everything that implies (it can time out, the other
service can be down, latency is now real and variable).
"""
import os
import httpx
from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Orders Service")
ORDERS: dict[int, dict] = {}
_next_id = 1

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")


async def fetch_user(user_id: int, client: httpx.AsyncClient) -> dict | None:
    try:
        resp = await client.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=2.0)
    except httpx.RequestError:
        # The Users service could be down, slow, or unreachable -- a Python
        # function call could NEVER fail this way. This is the core new
        # failure mode microservices introduce (see chapter 21: resilience).
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Users service unavailable",
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(user_id: int, amount_cents: int):
    global _next_id
    async with httpx.AsyncClient() as client:
        user = await fetch_user(user_id, client)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    order = {"id": _next_id, "user_id": user_id, "user_email": user["email"], "amount_cents": amount_cents}
    ORDERS[order["id"]] = order
    _next_id += 1
    return order


@app.get("/health")
def health():
    return {"status": "ok", "service": "orders"}
