"""
API-level tests: exercise the full stack (route -> auth -> db) through real
HTTP requests against the ASGI app, with an isolated in-memory database.
"""
import pytest
from app.tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio


async def test_create_and_list_own_notes(client):
    r = await client.post("/notes", params={"text": "buy milk"}, headers=auth_headers("ada@example.com"))
    assert r.status_code == 201

    r = await client.get("/notes", headers=auth_headers("ada@example.com"))
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["text"] == "buy milk"


async def test_notes_are_isolated_per_user(client):
    await client.post("/notes", params={"text": "ada's note"}, headers=auth_headers("ada@example.com"))
    await client.post("/notes", params={"text": "bob's note"}, headers=auth_headers("bob@example.com"))

    r = await client.get("/notes", headers=auth_headers("ada@example.com"))
    texts = [n["text"] for n in r.json()]
    assert texts == ["ada's note"]  # bob's note must NOT appear here


async def test_missing_auth_header_rejected(client):
    r = await client.get("/notes")
    assert r.status_code == 422  # required header missing -- FastAPI validation, not our 401 logic


async def test_cannot_delete_someone_elses_note(client):
    create = await client.post("/notes", params={"text": "private"}, headers=auth_headers("ada@example.com"))
    note_id = create.json()["id"]

    r = await client.delete(f"/notes/{note_id}", headers=auth_headers("bob@example.com"))
    assert r.status_code == 403

    r = await client.delete(f"/notes/{note_id}", headers=auth_headers("ada@example.com"))
    assert r.status_code == 204
