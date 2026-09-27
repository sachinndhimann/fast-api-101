# Exercise

Add a `Product` domain using the same layers (schema, model, repository, service, api router). Then add
a rule to `UserService`: a user can't be deleted if they have orders (stub
`OrderRepository.has_orders_for_user` returning `False` for now). Confirm you only touched the service
layer to add the rule.

## Interview-style scenario

Your team wants to swap Postgres for MongoDB in 6 months, one domain at a time, no downtime. Which
layers change, which stay untouched, and what would make the migration harder than it should be?
