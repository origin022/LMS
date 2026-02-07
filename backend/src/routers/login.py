from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm 
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.config import config 
from src.core.security import create_access_token, decode_access_token
from src.core.dep import get_session
from src.schemas.login import Token
from src.services.login import login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    login_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_session)
):
    return await login_user(
        email=login_data.username, 
        password=login_data.password, 
        db=db, 
        response=response 
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        path="/api/v1/auth/refresh", 
        samesite="lax"
    )
    return {"message": "تم تسجيل الخروج بنجاح"}

@router.post("/refresh")
async def refresh_access_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="انتهت الجلسة، سجل دخولك مرة أخرى")

    try:
        payload = decode_access_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="توكن غير صالح")
        
        user_id = payload.get("sub")
        new_access = create_access_token(data={"sub": user_id})

        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_access}",
            httponly=True,
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        return {"status": "success", "message": "تم تجديد الجلسة"}
        
    except Exception:
        raise HTTPException(status_code=401, detail="فشل تجديد الجلسة")