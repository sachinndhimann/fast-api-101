from fastapi import FastAPI
from app.users.router import router as users_router
from app.orders.router import router as orders_router

app = FastAPI(title="Chapter 17 - Modular Monolith")
app.include_router(users_router)
app.include_router(orders_router)

@app.get("/health")
def health():
    return {"status": "ok"}
