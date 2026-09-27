# Exercise

Add a second consumer bound to the `orders` exchange with routing key `order.#` (wildcard), logging
every order event to a separate `audit_log_q` — without touching `producer.py`.

## Interview-style scenario

Two `worker.py` instances consume from the same queue. A burst of 100 orders arrives. How does RabbitMQ
distribute them, and if one worker's machine is twice as fast, does it end up doing more work or does
load stay even?
