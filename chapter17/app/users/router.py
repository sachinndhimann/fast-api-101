from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

USERS = {1: {"id": 1, "name": "Ada", "email": "ada@example.com"}}

@router.get("/{user_id}")
def get_user(user_id: int):
    return USERS.get(user_id)
