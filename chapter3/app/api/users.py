"""
API layer: HTTP concerns only. Parses the request, calls the service, maps
the result (or exception) to an HTTP response. No business logic lives here --
if you find yourself writing an `if` about business rules in this file, it
belongs in the service layer instead.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserOut
from app.services.user_service import UserService, DuplicateEmailError
from app.dependencies.services import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        user = service.register_user(payload.name, payload.email)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserOut])
def list_users(service: UserService = Depends(get_user_service)):
    return service.list_users()
