"""
Fixed versions of every vulnerability in vulnerable.py, in the same order.
"""
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def fixed_get_user_by_name(conn: sqlite3.Connection, name: str):
    """
    PARAMETERIZED QUERY: the driver sends `name` as DATA, never as part of the
    SQL text -- injection payloads are treated as a literal string to match
    against, not as executable SQL syntax.
    """
    query = "SELECT * FROM users WHERE name = ?"
    return conn.execute(query, (name,)).fetchall()


def fixed_password_check(stored_hash: str, provided: str) -> bool:
    """HASHED PASSWORDS: see chapter 6. A leaked table reveals no usable plaintext passwords."""
    return pwd_context.verify(provided, stored_hash)


FIXED_CORS_CONFIG = {
    "allow_origins": ["https://app.example.com"],  # explicit allowlist, never "*" alongside credentials
    "allow_credentials": True,
}
