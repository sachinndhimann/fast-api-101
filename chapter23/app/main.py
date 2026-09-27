from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Note
from app.auth import get_current_user

app = FastAPI(title="Chapter 23 - Testing")


@app.post("/notes", status_code=status.HTTP_201_CREATED)
async def create_note(text: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    note = Note(owner_email=user["email"], text=text)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {"id": note.id, "text": note.text}


@app.get("/notes")
async def list_my_notes(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Only returns the CALLER's own notes -- an authorization concern worth its own test."""
    result = await db.execute(select(Note).where(Note.owner_email == user["email"]))
    notes = result.scalars().all()
    return [{"id": n.id, "text": n.text} for n in notes]


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if note.owner_email != user["email"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your note")
    await db.delete(note)
    await db.commit()
