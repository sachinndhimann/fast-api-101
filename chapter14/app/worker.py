"""
RabbitMQ consumer/worker. Run: python worker.py (requires `docker compose up -d rabbitmq`)

The API (see api.py) should NOT do this work synchronously -- see chapter 13.
This worker runs as a completely separate process, scaled independently of
the API.
"""
import json
import os
import time
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
MAX_RETRIES = 3


def handle_order_created(channel, method, properties, body):
    message = json.loads(body)
    retry_count = 0
    headers = properties.headers or {}
    retry_count = headers.get("x-retry-count", 0)

    try:
        print(f"Processing OrderCreated for order {message['order_id']} (attempt {retry_count + 1})")
        if message["order_id"] == 999:
            raise RuntimeError("Simulated processing failure for demo purposes")
        # ... send the welcome email here ...
        channel.basic_ack(delivery_tag=method.delivery_tag)  # ONLY ack after successful processing
        print("  -> done, acked")
    except Exception as exc:
        print(f"  -> failed: {exc}")
        if retry_count + 1 >= MAX_RETRIES:
            print("  -> max retries reached, sending to dead-letter queue")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            # republish with incremented retry count, then ack the original
            # (pika has no native per-message delay/backoff -- production
            # setups typically use a delayed-exchange plugin or a separate
            # "retry" queue with a TTL, not a raw requeue=True, which retries
            # instantly and can hot-loop a permanently-broken message)
            channel.basic_publish(
                exchange="orders",
                routing_key="order.created",
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={"x-retry-count": retry_count + 1},
                ),
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange="orders", exchange_type="topic", durable=True)
    channel.queue_declare(queue="order_created_q", durable=True)
    channel.queue_bind(exchange="orders", queue="order_created_q", routing_key="order.created")

    # Dead-letter queue: where permanently-failed messages land for later inspection.
    channel.queue_declare(queue="order_created_dlq", durable=True)

    channel.basic_qos(prefetch_count=1)  # don't hand a worker a new message until it acks the last one
    channel.basic_consume(queue="order_created_q", on_message_callback=handle_order_created, auto_ack=False)

    print("Worker started, waiting for messages. CTRL+C to exit.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
