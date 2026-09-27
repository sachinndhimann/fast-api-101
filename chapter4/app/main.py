from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repository import BookRepository

app = FastAPI(title="Chapter 4 - Database Integration")


@app.get("/books/naive")
async def books_naive(db: AsyncSession = Depends(get_db)):
    """Watch this one in an SQL query logger -- it fires 1 + N queries."""
    repo = BookRepository(db)
    books = await repo.list_naive()
    return [{"title": b.title, "author": b.author.name} for b in books]


@app.get("/books")
async def books_optimized(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = BookRepository(db)
    items, total = await repo.paginate(limit, offset)
    return {
        "items": [{"id": b.id, "title": b.title, "author": b.author.name} for b in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }
