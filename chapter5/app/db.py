class FakeDBSession:
    """Stand-in for a real DB session so this chapter doesn't need Postgres running."""
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True

def get_db():
    """
    A NEW session per request (not cached) -- this is the opposite pattern from
    get_settings(): Settings are safe to share across requests, DB sessions are
    NOT (each request must get its own, and it must be closed afterward).
    """
    db = FakeDBSession()
    try:
        yield db
    finally:
        db.close()
