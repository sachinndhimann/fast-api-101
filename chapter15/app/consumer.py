"""
Kafka consumer. Run: python consumer.py (requires `docker compose up -d zookeeper kafka`)

Multiple instances of this script with the SAME group.id form a consumer
GROUP: Kafka automatically splits the topic's partitions across them, so
scaling consumers is just "run more copies of this script."
"""
import json
import os
from confluent_kafka import Consumer, KafkaError

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def main():
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": "order-email-service",  # all consumers with this group.id share the topic's partitions
        "auto.offset.reset": "earliest",     # new consumer group starts from the beginning of the topic
        "enable.auto.commit": False,         # commit offsets manually, only after successful processing
    })
    consumer.subscribe(["orders"])

    print("Kafka consumer started, waiting for messages. CTRL+C to exit.")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise Exception(msg.error())

            event = json.loads(msg.value())
            print(f"[partition {msg.partition()} offset {msg.offset()}] {event}")
            # ... process event (e.g. send email) ...

            # AT-LEAST-ONCE semantics: if the process crashes between processing
            # and this commit, the message is redelivered on restart -- so
            # processing must be idempotent (safe to run twice).
            consumer.commit(msg)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
