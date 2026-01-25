from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import selectinload
from src.models.User import User
from src.core.security import verify_password, create_access_token 

async def login_user(email: str, password: str, db: AsyncSession):
    statement = (
        select(User)
        .where(User.email == email)
        .options(selectinload(User.roles)) 
    )
    
    result = await db.exec(statement)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الإيميل أو كلمة المرور غير صحيحة",
        )

    # 1. التحقق من الباسورد
    is_valid = await run_in_threadpool(verify_password, password, user.hashed_passwored)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الإيميل أو كلمة المرور غير صحيحة",
        )

    
    if user.state_id != 1:
        if user.state_id == 2:
            detail_msg = "حسابك بانتظار التفعيل. يرجى التأكد من بريدك الإلكتروني."
        elif user.state_id == 3:
            detail_msg = "تم حظر هذا الحساب، يرجى التواصل مع الإدارة."
        else:
            detail_msg = "حسابك غير نشط حالياً."
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=detail_msg
        )

    token = create_access_token(data={"sub": str(user.user_id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role_name": user.roles.roles_name if user.roles else "User"
        }
    }