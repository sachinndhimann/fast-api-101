"""
Chapter 13 - conceptual demo, no real broker yet (that's chapters 14/15).
Illustrates the SHAPE of synchronous vs asynchronous (message-based) service
communication using plain in-process function calls as a stand-in.
"""
import time


class EmailServiceSlow:
    """Stands in for a slow downstream dependency, e.g. a flaky email provider's API."""
    def send_welcome_email(self, user_email: str):
        time.sleep(0.3)  # simulates network latency to a third-party service
        return {"sent_to": user_email}


class SynchronousOrderService:
    """
    SYNCHRONOUS coupling: create_order() doesn't return until the email is
    sent. If the email service is slow or down, order creation is ALSO slow
    or down, even though "an order was placed" has nothing intrinsically to
    do with "an email was delivered."
    """
    def __init__(self, email_service: EmailServiceSlow):
        self.email_service = email_service

    def create_order(self, user_email: str) -> dict:
        order = {"id": 1, "status": "created"}
        self.email_service.send_welcome_email(user_email)  # BLOCKS here
        return order


class InMemoryQueue:
    """A toy stand-in for a real broker (RabbitMQ/Kafka, chapters 14-15)."""
    def __init__(self):
        self.messages: list[dict] = []

    def publish(self, message: dict):
        self.messages.append(message)

    def consume_all(self) -> list[dict]:
        drained, self.messages = self.messages, []
        return drained


class AsynchronousOrderService:
    """
    ASYNCHRONOUS coupling: create_order() publishes an OrderCreated event and
    returns IMMEDIATELY. A separate consumer (run whenever, by whoever) picks
    up the event and sends the email. Order creation's latency and
    availability are now independent of the email service's.
    """
    def __init__(self, queue: InMemoryQueue):
        self.queue = queue

    def create_order(self, user_email: str) -> dict:
        order = {"id": 1, "status": "created"}
        self.queue.publish({"event": "OrderCreated", "user_email": user_email})  # does NOT block
        return order
