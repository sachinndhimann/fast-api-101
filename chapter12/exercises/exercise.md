# Exercise

Add caching to `GET /products` (list), with a shorter TTL than individual products. Make `POST
/products` invalidate the list cache key too — note a bare `cache.invalidate(product_id)` won't cover
it since there's no single id for a list.

## Interview-style scenario

`/products/{id}` has a 5-minute TTL. A price change must be visible to all clients within 2 seconds, but
TTL alone can't guarantee that. What two approaches would you consider, and what does each cost?
