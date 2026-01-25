from typing import Annotated, List
from unittest import result
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from jose import JWTError
from src.models.Roles import Roles
from src.models.Roles_Permission import Roles_Permission
from src.models.User_Permission import User_Permission
from src.core.security import decode_access_token
from src.core.dep import get_session
from src.models.User import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Invalid Token Payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(user_id_str)

    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Token Expired or Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

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
        print(f"DEBUG: Token received is -> {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

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

        if self.required_permission not in user_role_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"not valid({current_user.roles.roles_name})"
            )

        stmt = select(User_Permission).where(
            User_Permission.user_id == current_user.user_id,
            User_Permission.is_granted == False 
        ).join(User_Permission.permission).where(
            User_Permission.permission.has(name=self.required_permission)
        )
        
       
        
        result = await db.exec(stmt)
        blacklisted = result.first()



        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"تم حظرك من استخدام صلاحية ({self.required_permission}) بسبب مخالفة القوانين"
            )

        return current_user