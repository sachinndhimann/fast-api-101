"""
Payments module -- deliberately has NO knowledge of Users or Orders. It only
knows how to charge a user_id an amount. This one-way dependency (orders ->
payments, never payments -> orders) is what "service boundaries" means inside
a modular monolith: modules can depend on each other, but the dependency
graph should be a DAG, not a tangle, or you don't actually have boundaries.
"""
PAYMENT_LEDGER: list[dict] = []


def charge(user_id: int, amount_cents: int) -> dict:
    # ... in a real system: call a payment processor, handle declines, etc ...
    PAYMENT_LEDGER.append({"user_id": user_id, "amount_cents": amount_cents})
    return {"success": True, "amount_cents": amount_cents}
