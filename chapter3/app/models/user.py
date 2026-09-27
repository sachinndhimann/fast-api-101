"""
In a real app this would be a SQLAlchemy model (see chapter 4). Kept as a
plain dataclass here so chapter 3 can focus purely on layering, without also
requiring a database.
"""
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
