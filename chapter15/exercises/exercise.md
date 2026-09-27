# Exercise

Publish `OrderCreated`, `OrderShipped`, `OrderCancelled` all to the `orders` topic, keyed by `order_id`.
Write a consumer that reconstructs an order's current status purely by replaying its event history from
the start — the core idea behind event sourcing.

## Interview-style scenario

Your `orders` topic has 6 partitions; your consumer group runs 3 instances. You scale to 8. What happens
to the 2 extra instances, and why doesn't adding more consumers than partitions help throughput?
