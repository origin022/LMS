from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, Response
from starlette.concurrency import run_in_threadpool
from src.models.User import User
from src.models.Roles import Roles
from src.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token
)

async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession
) -> User:

    stmt = (
        select(User)
        .where(User.email == email)
        .options(selectinload(User.roles))
    )

    result = await db.exec(stmt)
    user = result.first()

    if not user:
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")

    is_valid = await run_in_threadpool(
        verify_password,
        password,
        user.hashed_passwored
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")

    if user.state_id == 2:
        raise HTTPException(status_code=403, detail="حسابك بانتظار التفعيل، يرجى التحقق من بريدك الإلكتروني")
    elif user.state_id == 3:
        raise HTTPException(status_code=403, detail="تم حظر حسابك من قبل الإدارة")
    elif user.state_id != 1:
        raise HTTPException(status_code=403, detail="حسابك غير نشط حالياً")

    return user


def set_auth_cookies(response: Response, access: str, refresh: str):
    from src.core.config import config
    
    # In development, we might not use HTTPS, so we adjust cookie settings
    is_prod = config.ENVIRONMENT == "production"
    
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        samesite="lax" if not is_prod else "none",
        secure=is_prod,  # Must be True for samesite="none"
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="lax" if not is_prod else "none",
        secure=is_prod,
        path="/"
    )