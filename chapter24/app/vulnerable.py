"""
EDUCATIONAL ONLY -- every function in this file is intentionally insecure.
See fixed.py for the corrected version of each. Never copy patterns from
this file into real code.
"""
import sqlite3


def vulnerable_get_user_by_name(conn: sqlite3.Connection, name: str):
    """
    SQL INJECTION: the input is string-concatenated directly into the query.
    A name like `' OR '1'='1` returns EVERY row, and `'; DROP TABLE users;--`
    can destroy data outright, depending on driver/DB support for stacked queries.
    """
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return conn.execute(query).fetchall()


def vulnerable_password_check(stored_plaintext: str, provided: str) -> bool:
    """PLAINTEXT PASSWORDS: if this table is ever leaked, every password is immediately known."""
    return stored_plaintext == provided


VULNERABLE_CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,  # combined with "*", this is the CSRF-enabling misconfiguration from chapter 8
}
