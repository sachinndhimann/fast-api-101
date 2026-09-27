from fastapi import Depends, Header, HTTPException, status
from app.models import USERS, Role

def get_current_user(x_user_email: str = Header(..., description="Simulated auth -- see chapter 6 for real JWT auth")):
    user = USERS.get(x_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user


def require_role(*allowed: Role):
    """
    Dependency FACTORY: returns a dependency configured for specific roles.
    Usage: Depends(require_role(Role.admin, Role.manager))
    """
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return checker
