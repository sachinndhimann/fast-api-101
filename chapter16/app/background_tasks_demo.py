"""
FastAPI's built-in BackgroundTasks: runs AFTER the response is sent, IN THE
SAME PROCESS as the API. Zero infrastructure needed -- but if this process
restarts or crashes before the task runs, the task is just gone. No retry,
no persistence, no cross-process scaling.
"""
import time
from fastapi import FastAPI, BackgroundTasks

app = FastAPI(title="Chapter 16 - Background Jobs")

SENT_EMAILS: list[str] = []  # in-memory, purely so the demo/tests can observe it


def send_welcome_email(user_email: str):
    time.sleep(0.05)  # simulated latency
    SENT_EMAILS.append(user_email)
    print(f"[background] sent welcome email to {user_email}")


@app.post("/signup")
def signup(user_email: str, background_tasks: BackgroundTasks):
    """
    The response returns to the client immediately; send_welcome_email runs
    AFTER, still within this same worker process.

    Appropriate for: cheap, best-effort, non-critical work where losing it
    occasionally on a crash/restart is acceptable (e.g. a non-essential log,
    a cache warm, a Slack notification -- NOT charging a card or anything
    that must survive a process restart).
    """
    background_tasks.add_task(send_welcome_email, user_email)
    return {"message": "signed up", "email": user_email}
