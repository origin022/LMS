
from datetime import datetime, timedelta, timezone 
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlmodel import select

from .config import config  

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) :

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) :
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire , "type": "access"})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) :

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("invalied token") from e



def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"}) 
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)





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