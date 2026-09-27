import sqlite3
import pytest
from app.vulnerable import vulnerable_get_user_by_name, vulnerable_password_check
from app.fixed import fixed_get_user_by_name, fixed_password_check, pwd_context


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, secret TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'alice', 'alice-secret')")
    conn.execute("INSERT INTO users VALUES (2, 'bob', 'bob-secret')")
    conn.commit()
    yield conn
    conn.close()


def test_vulnerable_query_is_actually_exploitable(db):
    """
    Proves the vulnerability is REAL, not theoretical: this classic injection
    payload returns ALL rows instead of zero, despite no user named this.
    """
    payload = "nonexistent' OR '1'='1"
    rows = vulnerable_get_user_by_name(db, payload)
    assert len(rows) == 2  # BOTH users leaked, despite querying for a name that doesn't exist


def test_fixed_query_rejects_the_same_payload(db):
    payload = "nonexistent' OR '1'='1"
    rows = fixed_get_user_by_name(db, payload)
    assert len(rows) == 0  # correctly treated as a literal (non-matching) string, not SQL syntax


def test_vulnerable_password_check_leaks_via_plaintext_comparison():
    # There's no meaningful "attack" to demonstrate on the check itself --
    # the vulnerability is that `stored_plaintext` exists in storage AT ALL.
    assert vulnerable_password_check("hunter2", "hunter2") is True
    # If this table were ever dumped, "hunter2" is immediately usable -- no cracking required.


def test_fixed_password_check_never_stores_plaintext():
    hashed = pwd_context.hash("hunter2")
    assert hashed != "hunter2"                      # stored value is not the password itself
    assert fixed_password_check(hashed, "hunter2") is True
    assert fixed_password_check(hashed, "wrong") is False
