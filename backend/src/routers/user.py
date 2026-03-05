
from fastapi import APIRouter, BackgroundTasks, Depends
from src.services.EmailSe import EmailService
from src.core.dep import get_session 
from src.schemas.user import UserCreate, UserInvitationRegister, UserRead
from src.services.user import  create_new_user, register_invited_user 
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends


router = APIRouter( ) 
@router.post("/register", response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_session)
):
    user, raw_token = await create_new_user(user_data=user_data, db=db)

    background_tasks.add_task( 
        EmailService.send_universal_mail,
        to_email=user.email,
        token=raw_token,
        subject="تفعيل حسابك في المنصة",
        template="verify_account.html",
        route="verify-email"
    )

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role_name": user.roles.roles_name
    }



@router.post("/register-by-token", response_model=UserRead)
async def register_by_token(
    user_data: UserInvitationRegister, 
    db: AsyncSession = Depends(get_session)
):
    return await register_invited_user(db, user_data)



@router.get("/verify-email")
async def verify_email(
    token: str, 
    db: AsyncSession = Depends(get_session)
):
    return await EmailService.verify_user_email(token, db)
