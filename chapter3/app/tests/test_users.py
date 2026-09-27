"""
Because business logic lives in the service layer and the service depends only
on an abstract repository, we can unit test it with zero HTTP and zero DB.
"""
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService, DuplicateEmailError
import pytest


def test_register_and_get_user():
    service = UserService(UserRepository())
    user = service.register_user("Ada", "ada@example.com")
    assert user.id == 1
    assert service.get_user(1).name == "Ada"


def test_duplicate_email_rejected():
    service = UserService(UserRepository())
    service.register_user("Ada", "ada@example.com")
    with pytest.raises(DuplicateEmailError):
        service.register_user("Ada2", "ada@example.com")
