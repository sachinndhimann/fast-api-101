# Exercise

Add a `notifications` module that sends an order-confirmation notification after a successful order.
Decide and justify: synchronous function call (like `payments`) or a published event (chapters 13-14)?
What makes this different from the payment charge, which stayed synchronous?

## Interview-style scenario

`payments` needs to scale to 50x the volume of `users`+`orders` combined, due to a new partner
integration. Given this chapter's module boundaries, what would extracting `payments` into its own
service require changing — and what would it NOT require changing, specifically because of the boundary?
