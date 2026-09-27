"""
FastAPI app that PUBLISHES to RabbitMQ instead of doing slow work inline.
"""
from fastapi import FastAPI
from app.producer import publish_order_created

app = FastAPI(title="Chapter 14 - RabbitMQ")


@app.post("/orders")
def create_order(user_email: str):
    order_id = 1  # in a real app, this comes from the database (chapter 4)
    publish_order_created(order_id, user_email)  # returns fast; email is sent by worker.py, separately
    return {"id": order_id, "status": "created"}
