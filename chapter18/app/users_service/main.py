"""
Standalone Users service. Its own process, its own port, its own database
(in a real deployment) -- contrast with chapter 17 where this was just a
Python module in the same process.
"""
from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Users Service")
USERS = {1: {"id": 1, "name": "Ada", "email": "ada@example.com"}}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.get("/health")
def health():
    return {"status": "ok", "service": "users"}
