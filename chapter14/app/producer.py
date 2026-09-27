"""
RabbitMQ producer. Run: python producer.py (requires `docker compose up -d rabbitmq`)
"""
import json
import os
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def publish_order_created(order_id: int, user_email: str):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Exchange: routes messages to queues based on routing_key + binding rules.
    # "topic" exchange lets bindings use wildcards (order.*, order.#).
    channel.exchange_declare(exchange="orders", exchange_type="topic", durable=True)

    # Queue: durable=True survives a broker restart; without it, a restart
    # silently drops the queue and any unconsumed messages in it.
    channel.queue_declare(queue="order_created_q", durable=True)
    channel.queue_bind(exchange="orders", queue="order_created_q", routing_key="order.created")

    body = json.dumps({"order_id": order_id, "user_email": user_email})
    channel.basic_publish(
        exchange="orders",
        routing_key="order.created",
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,  # persistent: survives broker restart, paired with a durable queue
            content_type="application/json",
        ),
    )
    print(f"Published OrderCreated: {body}")
    connection.close()


if __name__ == "__main__":
    publish_order_created(order_id=1, user_email="ada@example.com")
