from fastapi.testclient import TestClient
from app.background_tasks_demo import app, SENT_EMAILS

client = TestClient(app)

def test_signup_triggers_background_email():
    SENT_EMAILS.clear()
    r = client.post("/signup", params={"user_email": "ada@example.com"})
    assert r.status_code == 200
    # TestClient runs background tasks synchronously before returning control,
    # which is convenient for testing but NOT how it behaves in a real running
    # server (there, it genuinely runs after the response is sent over the wire).
    assert SENT_EMAILS == ["ada@example.com"]
