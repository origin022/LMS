from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm 
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.dep import get_session
from src.schemas.login import Token
from src.services.login import login_user

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=Token)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_session)
):
    return await login_user(login_data.username, login_data.password, db)