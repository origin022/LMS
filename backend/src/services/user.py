import uuid
from sqlmodel import  select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from src.models.VerificationTok import VerificationToken
from src.services.EmailSe import EmailService
from src.models.User import User
from src.schemas.user import UserCreate, UserInvitationRegister
from src.core.security import hash_password
from src.models.Invitation import Invitation
from src.core.security import hash_password 
from datetime import datetime, timedelta, timezone


async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession
) -> User:

    result = await db.exec(select(User).where(User.email == user_data.email))
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا الإيميل مسجل بالفعل"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_passwored=hash_password(user_data.password),
        phone=user_data.phone,
        roles_id=user_data.roles_id,
        state_id=2, 
    )
    db.add(new_user)

    raw_token = str(uuid.uuid4())
    
   
    expires = (datetime.now(timezone.utc) + timedelta(hours=24)).replace(tzinfo=None)

    verification_entry = VerificationToken(
        token=raw_token,
        email=new_user.email,
        expires_at=expires, 
        type="magic_link"
    )
    db.add(verification_entry)

    await db.commit()

    await db.refresh(new_user)
    
    stmt = (
        select(User)
        .where(User.user_id == new_user.user_id)
        .options(selectinload(User.roles))
    )
    res = await db.exec(stmt)
    return res.one() , raw_token

async def register_invited_user(db: AsyncSession, user_data: UserInvitationRegister):
    statement = select(Invitation).where(Invitation.token == user_data.token)
    result = await db.exec(statement)
    invitation = result.first()

    if not invitation:
        raise HTTPException(status_code=404, detail="رابط الدعوة غير موجود")

    current_time_utc = datetime.now(timezone.utc).replace(tzinfo=None) 

    if invitation.expires_at < current_time_utc:
         raise HTTPException(status_code=400, detail="انتهت صلاحية الرابط")
        
    if invitation.is_used:
        raise HTTPException(status_code=400, detail="تم استخدام الدعوة مسبقاً")

    user_exists_stmt = select(User).where(User.email == invitation.email)
    user_exists_res = await db.exec(user_exists_stmt)
    if user_exists_res.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="هذا الإيميل مسجل بالفعل، ربما أكملت التسجيل مسبقاً"
        )

    new_user = User(
        name=user_data.name,
        email=invitation.email,
        hashed_passwored=hash_password(user_data.password),
        roles_id=invitation.role_id, 
        state_id=1, 
        phone=user_data.phone
    )

    db.add(new_user)
    invitation.is_used = True
        
    db.add(invitation)
        
    await db.commit()
    await db.refresh(new_user)
    return new_user