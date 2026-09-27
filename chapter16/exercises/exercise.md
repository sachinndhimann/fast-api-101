# Exercise

Reimplement `/signup` using `app/celery_example.py`'s task instead of `BackgroundTasks`. Simulate a
crash: kill the FastAPI process right after calling the endpoint, before a worker has run. Confirm the
task still completes once a worker eventually runs — unlike the `BackgroundTasks` version.

## Interview-style scenario

Your team is debating `BackgroundTasks` vs Celery for password-reset emails. What's the concrete failure
mode that should decide this — not in the abstract, but "if X happens, what does the user experience"?
