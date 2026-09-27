from fastapi import FastAPI, Depends, HTTPException, status
from app.deps import get_current_user, require_role
from app.models import Role, PROFILES, USERS

app = FastAPI(title="Chapter 7 - Authorization (RBAC)")


@app.get("/profiles/{email}")
def read_own_profile(email: str, user: dict = Depends(get_current_user)):
    """
    RESOURCE-LEVEL authorization: not just "are you logged in" but "is this
    YOUR resource". A user can read their own profile; role alone (RBAC)
    doesn't capture this -- it's an ownership check, sometimes called ABAC
    (attribute-based: the attribute here is 'is the resource owner == caller').
    """
    if email != user["email"] and user["role"] not in (Role.manager, Role.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only read your own profile")
    profile = PROFILES.get(email)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@app.get("/team-data")
def read_team_data(user: dict = Depends(require_role(Role.manager, Role.admin))):
    """Manager can read team data (RBAC: role check only, no ownership check needed)."""
    teammates = [u for u in USERS.values() if u["team"] == user["team"]]
    return {"team": user["team"], "members": [u["email"] for u in teammates]}


@app.delete("/users/{email}")
def delete_user(email: str, admin: dict = Depends(require_role(Role.admin))):
    """Admin can manage users -- pure RBAC, no ownership dimension."""
    if email not in USERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    del USERS[email]
    return {"message": f"{email} deleted"}
