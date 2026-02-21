from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status,Response
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import selectinload
from src.core.config import config
from src.models.User import User
from src.core.security import create_refresh_token, verify_password, create_access_token 

async def login_user(email: str, password: str, db: AsyncSession, response: Response):
    statement = (
        select(User)
        .where(User.email == email)
        .options(selectinload(User.roles)) 
    )
    
    result = await db.exec(statement)
    db_user = result.first() 

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الإيميل أو كلمة المرور غير صحيحة",
        )

    is_valid = await run_in_threadpool(verify_password, password, db_user.hashed_passwored)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="خطأ في البيانات")

    if db_user.state_id != 1:
        raise HTTPException(status_code=403, detail="الحساب غير نشط")

    access_token = create_access_token(data={"sub": str(db_user.user_id),"type": "access"}
)

    refresh_token = create_refresh_token(data={"sub": str(db_user.user_id),"type": "refresh"}
)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True, 
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
        samesite="lax",
        secure=False
    )

    return {
        "token_type": "bearer",
        "user": {
            "user_id": db_user.user_id,
            "email": db_user.email,
            "role_name": db_user.roles.roles_name if db_user.roles else "User"
        }
    }