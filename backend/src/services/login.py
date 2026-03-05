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
        raise HTTPException(status_code=401, detail="Invalid credentials")

    is_valid = await run_in_threadpool(
        verify_password,
        password,
        user.hashed_passwored
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.state_id != 1:
        raise HTTPException(status_code=403, detail="Account disabled")

    return user


def set_auth_cookies(response: Response, access: str, refresh: str):

    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )