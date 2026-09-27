# Exercise

Add a Payments service (port 8003); update Orders to call it, mirroring chapter 17's in-process
`charge()`. Then make Payments artificially slow (`await asyncio.sleep(5)`) and observe Orders' response
time with no timeout configured, then add one and observe the difference.

## Interview-style scenario

In chapter 17's monolith, order creation and payment charging were one atomic operation. Here, what
happens if the charge succeeds but the network response back to Orders times out before Orders can mark
the order paid? What inconsistency results, and what would you add to detect and correct it?
