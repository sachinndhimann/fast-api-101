"""
V1: synchronous in-process "charge". See docs/evolution.md for how this
function's CALLERS change across versions while its own signature stays
stable -- that stability is what makes the later evolutions non-disruptive.
"""
PAYMENT_LEDGER: list[dict] = []

def charge(order_id: int, amount_cents: int) -> dict:
    PAYMENT_LEDGER.append({"order_id": order_id, "amount_cents": amount_cents})
    return {"success": True}
