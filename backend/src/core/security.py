from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import config
from sqlalchemy import select

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
    pk_name = model.__table__.primary_key.columns.keys()[0]
    statement = select(model).where(getattr(model, pk_name) == obj_id)
    result = await db.exec(statement)
    obj = result.first()

    if not obj:
        raise HTTPException(status_code=404, detail=f"الـ {model.__name__} غير موجود")

    if getattr(obj, user_field) != current_user.user_id:
        raise HTTPException(
            status_code=403, 
            detail="لا تملك صلاحية الوصول لهذا السجل (ليس ملكك)"
        )

    return obj
