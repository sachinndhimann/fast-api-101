from fastapi import FastAPI
from app.products.router import router as products_router
from app.orders.router import router as orders_router

app = FastAPI(title="Order Management Platform - V1: Modular Monolith")
app.include_router(products_router)
app.include_router(orders_router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "v1-monolith"}
