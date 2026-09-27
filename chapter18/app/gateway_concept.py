"""
API Gateway concept sketch (not a full implementation -- in production you'd
use something like Kong, an AWS API Gateway, Nginx, or Envoy). This shows the
SHAPE of what a gateway does: routes external requests to the right internal
service, so external clients only ever talk to ONE hostname.
"""
import httpx
from fastapi import FastAPI, Request

app = FastAPI(title="Chapter 18 - API Gateway (sketch)")

ROUTES = {
    "/users": "http://localhost:8001",
    "/orders": "http://localhost:8002",
}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway(path: str, request: Request):
    for prefix, target in ROUTES.items():
        if f"/{path}".startswith(prefix):
            async with httpx.AsyncClient() as client:
                resp = await client.request(
                    request.method,
                    f"{target}/{path}",
                    params=dict(request.query_params),
                    content=await request.body(),
                )
            return resp.json()
    return {"error": "no route matches"}, 404
