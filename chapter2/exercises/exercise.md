# Exercise

Rewrite every endpoint in `app/bad_example.py` to be REST-compliant: correct HTTP methods, correct
status codes, pagination on the collection endpoint, and a consistent error envelope. Compare against
`app/good_example.py`.

## Interview-style scenario

Design the URL structure and methods for a "like" feature on a post: a user can like once, unlike, and
check like-status. Is "like" a resource? What method creates it? What happens on a double "like" call —
error, or idempotent?
