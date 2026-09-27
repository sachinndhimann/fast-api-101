# Exercise

Add a `Review` model (`book_id`, `rating`, `comment`) and `GET /books/{id}/reviews`. Then extend
`list_with_authors` to also eager-load reviews per book in a bounded number of queries — try composing
two `selectinload()` calls and count the queries with `echo=True`.

## Interview-style scenario

An endpoint that took 50ms now takes 4s after a migration added 10,000 rows to a related table. The
same query run directly in `psql` is still fast. What do you check first?
(Hint: query count, not query latency.)
