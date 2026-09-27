from fastapi import APIRouter, HTTPException, status
from app.users.router import USERS
from app.payments.service import charge

router = APIRouter(prefix="/orders", tags=["orders"])
ORDERS: dict[int, dict] = {}
_next_id = 1


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(user_id: int, amount_cents: int):
    """
    MODULAR MONOLITH pattern: orders calls INTO payments as a normal Python
    function call (app.payments.service.charge), not over HTTP or a queue.
    This is the "internal API" chapter 17 talks about -- a clean function
    boundary between modules that happen to live in the same deployable, same
    process, same database.
    """
    global _next_id
    if user_id not in USERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    charge_result = charge(user_id, amount_cents)
    if not charge_result["success"]:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment failed")

    order = {"id": _next_id, "user_id": user_id, "amount_cents": amount_cents, "status": "paid"}
    ORDERS[order["id"]] = order
    _next_id += 1
    return order


@router.get("/{order_id}")
def get_order(order_id: int):
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
