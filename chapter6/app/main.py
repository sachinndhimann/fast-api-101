from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import JWTError

from app.security import (
    create_access_token, create_refresh_token, verify_password, decode_token,
)
from app.store import register, get_user, VALID_REFRESH_TOKENS
from app.deps import get_current_user

app = FastAPI(title="Chapter 6 - JWT Authentication")


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterIn):
    try:
        register(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {"email": payload.email}


@app.post("/auth/login", response_model=TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2PasswordRequestForm expects x-www-form-urlencoded `username`+`password`
    (it uses `username` even though we treat it as an email) -- this is what
    makes Swagger UI's built-in "Authorize" button work out of the box.
    """
    user = get_user(form.username)
    if user is None or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access = create_access_token(subject=user["email"])
    refresh = create_refresh_token(subject=user["email"])
    VALID_REFRESH_TOKENS.add(refresh)
    return TokenPair(access_token=access, refresh_token=refresh)


@app.post("/auth/refresh", response_model=TokenPair)
def refresh_token(refresh_token: str):
    """
    Refresh token ROTATION: the old refresh token is invalidated and a new one
    issued alongside the new access token. If a refresh token is ever stolen
    and used, rotation limits the attacker to one use before the legitimate
    owner's next refresh call reveals the token was already used elsewhere
    (a "reuse detection" scheme -- not implemented here, but this allowlist is
    the seam where you would revoke the whole family of tokens on reuse).
    """
    if refresh_token not in VALID_REFRESH_TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked refresh token")
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    VALID_REFRESH_TOKENS.discard(refresh_token)  # rotate: old one is now dead
    email = payload["sub"]
    new_access = create_access_token(subject=email)
    new_refresh = create_refresh_token(subject=email)
    VALID_REFRESH_TOKENS.add(new_refresh)
    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@app.post("/auth/logout")
def logout(refresh_token: str):
    """Revocation: JWTs are stateless by design, so 'logout' only works if you track issued tokens somewhere."""
    VALID_REFRESH_TOKENS.discard(refresh_token)
    return {"message": "Logged out"}


@app.get("/users/me")
def read_current_user(user: dict = Depends(get_current_user)):
    return {"email": user["email"]}
