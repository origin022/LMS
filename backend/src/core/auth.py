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
from src.core.security import decode_access_token
from src.core.dep import get_session
from src.models.User import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_session),
    token_with_bearer: str = Depends(oauth2_scheme)
) -> User:
    token_with_bearer = request.cookies.get("access_token")
    
    if not token_with_bearer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="جلسة العمل انتهت، يرجى تسجيل الدخول",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = token_with_bearer.replace("Bearer ", "")

    try:
        payload = decode_access_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="نوع التوكن غير صالح للوصول",
            )

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="فشل التحقق من هوية المستخدم",
            )
        
        user_id = int(user_id_str)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="التوكن منتهي الصلاحية أو غير صالح",
            headers={"WWW-Authenticate": "Bearer"},
        )

    statement = (
        select(User)
        .where(User.user_id == user_id)
        .options(
            selectinload(User.roles)
            .selectinload(Roles.roles_permission)
            .selectinload(Roles_Permission.permission)
        )
    )
    
    result = await db.exec(statement)
    user = result.first()

    if isinstance(user, tuple):
        user = user[0]

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود في النظام",
        )

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
        if current_user.state_id != 1:  
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="حسابك معطل، يرجى التواصل مع الدعم"
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