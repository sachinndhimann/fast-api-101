"""
Celery: a task queue with its own broker (commonly Redis or RabbitMQ) and
persistent, retryable tasks -- unlike BackgroundTasks, tasks survive an API
process restart (they live in the broker until a worker picks them up) and
can be retried automatically.

This file shows the SHAPE of Celery usage; running it for real requires:
    pip install celery
    celery -A app.celery_example worker --loglevel=info
"""
from celery import Celery

celery_app = Celery("chapter16", broker="redis://localhost:6379/1", backend="redis://localhost:6379/2")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_welcome_email_task(self, user_email: str):
    try:
        print(f"[celery worker] sending welcome email to {user_email}")
        # ... actual email sending, may raise on failure ...
    except Exception as exc:
        raise self.retry(exc=exc)  # retries with backoff, persisted across worker restarts


# In your FastAPI route:
#   from app.celery_example import send_welcome_email_task
#   @app.post("/signup")
#   def signup(user_email: str):
#       send_welcome_email_task.delay(user_email)   # enqueues, returns immediately
#       return {"message": "signed up"}
