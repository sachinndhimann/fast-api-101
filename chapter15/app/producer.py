"""
Kafka producer. Run: python producer.py (requires `docker compose up -d zookeeper kafka`)
"""
import json
import os
from confluent_kafka import Producer

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [partition {msg.partition()}] at offset {msg.offset()}")


def publish_order_event(order_id: int, user_email: str, event_type: str = "OrderCreated"):
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    payload = json.dumps({"event": event_type, "order_id": order_id, "user_email": user_email})

    # KEY matters: Kafka guarantees ordering only WITHIN a partition, and the
    # key determines which partition a message lands in (same key -> same
    # partition, always). Keying by order_id means all events for one order
    # are strictly ordered relative to each other, even with many partitions.
    producer.produce(
        topic="orders",
        key=str(order_id),
        value=payload,
        callback=delivery_report,
    )
    producer.flush()  # blocks until delivery is confirmed or times out


if __name__ == "__main__":
    publish_order_event(order_id=1, user_email="ada@example.com")
