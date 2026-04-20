from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.dep import get_session
from src.core.security import create_access_token, create_refresh_token, decode_token, limiter, AUTH_LIMIT, SENSITIVE_LIMIT
from src.services.login import authenticate_user, set_auth_cookies

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
@limiter.limit(AUTH_LIMIT)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):

    user = await authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=db
    )

    access = create_access_token(user.user_id)
    refresh = create_refresh_token(user.user_id)

    set_auth_cookies(response, access, refresh)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.roles.roles_name if user.roles else None,
        "access_token": access  # Decisive token for mobile
    }


@router.post("/refresh")
@limiter.limit(SENSITIVE_LIMIT)
async def refresh(
    request: Request,
    response: Response
):

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401)

    payload = decode_token(refresh_token, expected_type="refresh")
    user_id = int(payload.get("sub"))

    new_access = create_access_token(user_id)

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return {"status": "refreshed"}


@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return {"message": "Logged out"}