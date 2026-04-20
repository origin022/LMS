from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from jose import JWTError
from src.models import Permission
from src.models.Roles import Roles
from src.models.Roles_Permission import Roles_Permission
from src.models.User_Permission import User_Permission
from src.core.security import decode_token
from src.core.dep import get_session
from src.models.User import User
from fastapi.security import OAuth2PasswordBearer
from typing import Optional



async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> User:
    


    # Try to get token from cookies or Authorization header
    token = request.cookies.get("access_token")
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401)

    payload = decode_token(token, expected_type="access")
    user_id = int(payload.get("sub"))

    stmt = (
        select(User)
        .where(User.user_id == user_id)
        .options(
            selectinload(User.roles)
            .selectinload(Roles.roles_permission)
            .selectinload(Roles_Permission.permission)
        )
    )

    result = await db.exec(stmt)
    user = result.first()

    if not user:
        raise HTTPException(status_code=401)

    return user
class PermissionChecker:
    def __init__(self, required_permissions: str | list[str]):
        if isinstance(required_permissions, str):
            self.required_permissions = [required_permissions]
        else:
            self.required_permissions = required_permissions

    async def __call__(
        self, 
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
    ):
        if current_user.state_id == 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="حسابك بانتظار التفعيل، يرجى التحقق من بريدك الإلكتروني"
            )
        elif current_user.state_id == 3:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="تم حظر حسابك نهائياً من قبل الإدارة"
            )
        elif current_user.state_id != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="حسابك غير نشط حالياً، يرجى مراجعة الدعم"
            )

        user_role_permissions = []
        if current_user.roles:
            for rp in current_user.roles.roles_permission:
                user_role_permissions.append(rp.permission.name)

        if not any(p in user_role_permissions for p in self.required_permissions):
            role_name = current_user.roles.roles_name if current_user.roles else "No Role"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"ليس لديك صلاحية كافية ({role_name})"
            )

        stmt = select(User_Permission).join(Permission).where(
            User_Permission.user_id == current_user.user_id,
            Permission.name.in_(self.required_permissions) 
        )
        result = await db.exec(stmt)
        blacklisted = result.first()

        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="تم حظرك من استخدام هذه الصلاحية خصيصاً"
            )

        return current_user






async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session)
) -> Optional[User]:
    try:
        return await get_current_user(request, db) 
    except Exception:
        return None