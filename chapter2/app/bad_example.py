"""
Chapter 2 - BAD API design. Do not copy this. See good_example.py for the fix.
"""
from fastapi import FastAPI

app = FastAPI()

# Verb in the URL -- URLs should name resources, not actions.
@app.get("/getAllUsers")
def get_all_users():
    ...

# Action-as-endpoint instead of using HTTP method semantics.
@app.post("/deleteUser")
def delete_user(user_id: int):
    ...

# Non-plural, inconsistent resource naming across endpoints.
@app.get("/user/{id}")
def get_user(id: int):
    ...

# Returns 200 for a request that actually failed.
@app.post("/user/create")
def create_user_bad(name: str):
    if not name:
        return {"error": "name required"}, 200  # WRONG: should be 400/422
    return {"ok": True}

# No pagination on a collection that could have millions of rows.
@app.get("/orders/all")
def all_orders():
    return {"orders": "... every single order, unbounded ..."}
