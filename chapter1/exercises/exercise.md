# Exercise

Extend `app/main.py` with an `Order` resource:

1. `POST /orders` takes `product_id` and `quantity`; look up the product, reject with 400 if the
   product doesn't exist or is out of stock.
2. `GET /orders/{id}` returns the order with the product's *current* name and price embedded, not
   just `product_id` — your first response shape that isn't a 1:1 mirror of storage.
3. `GET /orders` supports a `min_total_cents` query filter.

## Interview-style scenario

A teammate's PR adds a new required field (no default) to `ProductCreate`. What breaks, for whom, and
when — for a cached Swagger client? For a mobile app on a 6-month-old schema that can't be force
updated? How would you introduce the field instead? (Revisit after chapter 2 and chapter 19.)
