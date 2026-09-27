"""
Chapter 2 - GOOD API design, fixing every issue in bad_example.py.
"""
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    name: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


# Resource-oriented, plural, consistent nouns. The HTTP method carries the verb.
@app.get("/users")
def list_users(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Pagination is not optional for any collection that can grow unbounded."""
    return {"items": [], "limit": limit, "offset": offset, "total": 0}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    """Validation failures return 422 automatically; business rule failures return 400/409."""
    return {"id": 1, "name": payload.name}


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """DELETE is a method, not an action verb baked into the path."""
    return None


@app.get("/orders")
def list_orders(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return {"items": [], "limit": limit, "offset": offset, "total": 0}
