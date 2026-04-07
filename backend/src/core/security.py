from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import config
from sqlalchemy import select
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Response


limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# Rate limit constants
AUTH_LIMIT = "5/minute"
SENSITIVE_LIMIT = "10/minute"
PUBLIC_LIMIT = "60/minute"
HEAVY_LIMIT = "20/minute"
DEFAULT_LIMIT = "100/minute"

async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={"detail": "لقد تجاوزت الحد المسموح به من الطلبات. يرجى المحاولة لاحقاً."},
    )

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "type": token_type
    })
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != expected_type:
        raise HTTPException(status_code=401, detail="Invalid token type")

    return payload



async def get_owned_obj(db, model, obj_id, current_user, user_field="user_id"):
    statement = select(model).where(getattr(model, model.__table__.primary_key.columns.keys()[0]) == obj_id)

    result = await db.execute(statement)
    obj = result.scalars().first()

    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

    if getattr(obj, user_field) != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return obj