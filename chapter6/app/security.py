import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "dev-only-change-me"   # In production: a long random value from a secrets manager, never in code.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    """
    JWT structure: header.payload.signature
      - header:    {"alg": "HS256", "typ": "JWT"}          (base64, not encrypted -- never put secrets here)
      - payload:   {"sub": ..., "exp": ..., "type": ...}    (base64, ALSO NOT ENCRYPTED -- anyone can read it)
      - signature: HMAC(header.payload, SECRET_KEY)         (this is the only part that prevents tampering)
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
        "jti": str(uuid.uuid4()),  # unique ID per token: makes every token distinct even if issued
                                    # in the same second, and is what you'd log/blocklist on revocation
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    return create_token(subject, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access")


def create_refresh_token(subject: str) -> str:
    return create_token(subject, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str) -> dict:
    """Raises JWTError on bad signature, malformed token, or expiry -- caller maps this to a 401."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
