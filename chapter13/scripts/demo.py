import sys, time
sys.path.insert(0, "..")
from app.sync_vs_async import SynchronousOrderService, AsynchronousOrderService, EmailServiceSlow, InMemoryQueue

sync_svc = SynchronousOrderService(EmailServiceSlow())
t0 = time.perf_counter()
sync_svc.create_order("a@b.com")
print("sync:", round(time.perf_counter() - t0, 3), "s")

q = InMemoryQueue()
async_svc = AsynchronousOrderService(q)
t0 = time.perf_counter()
async_svc.create_order("a@b.com")
print("async:", round(time.perf_counter() - t0, 3), "s")
print("pending messages:", q.consume_all())
