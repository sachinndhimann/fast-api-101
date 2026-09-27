from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book, Author


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_naive(self) -> list[Book]:
        """
        BAD: this triggers the N+1 problem the moment calling code accesses
        `book.author.name` for each book, if Book.author isn't eager-loaded --
        one query for the books, then one more query PER BOOK for its author.
        """
        result = await self.db.execute(select(Book))
        return list(result.scalars().all())

    async def list_with_authors(self) -> list[Book]:
        """
        GOOD: selectinload issues exactly 2 queries total, regardless of how
        many books there are -- one for books, one for all their authors in a
        single `WHERE author_id IN (...)` query.
        """
        result = await self.db.execute(select(Book).options(selectinload(Book.author)))
        return list(result.scalars().all())

    async def paginate(self, limit: int, offset: int) -> tuple[list[Book], int]:
        """Always return total count alongside a page -- clients need it to render pagination UI."""
        items_result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).limit(limit).offset(offset)
        )
        count_result = await self.db.execute(select(func.count()).select_from(Book))
        return list(items_result.scalars().all()), count_result.scalar_one()

    async def create(self, title: str, price_cents: int, author_id: int) -> Book:
        book = Book(title=title, price_cents=price_cents, author_id=author_id)
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book
