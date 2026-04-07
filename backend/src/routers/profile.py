from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.auth import PermissionChecker, get_current_user
from src.core.dep import get_session
from src.schemas.profile import ReadProfile, UpdateProfile , ProfileUpdateResponse
from src.services.profile import ProfileService
from src.models.User import User
from src.core.security import limiter, SENSITIVE_LIMIT, DEFAULT_LIMIT, HEAVY_LIMIT

allow_profile = PermissionChecker(["Manage Profile"])

router = APIRouter()


@router.get("/profile")
@limiter.limit(DEFAULT_LIMIT)
async def get_my_profile(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    profile = await ProfileService.get_profile(db, current_user.user_id)

    role_name = current_user.roles.roles_name if current_user.roles else ""

    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "bio": profile.bio if profile else "",
        "picture": True if profile and profile.profile_picture_data else False,
        "role": role_name
    }


@router.patch(
    "/profile",
    status_code=200,
    response_model=ProfileUpdateResponse,
    dependencies=[Depends(allow_profile)]
)
@limiter.limit(SENSITIVE_LIMIT)
async def update_profile(
    request: Request,
    data: UpdateProfile,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    profile = await ProfileService.update_profile_info(
        db,
        current_user.user_id,
        data
    )

    if not profile:
        raise HTTPException(status_code=404, detail="الصفحة الشخصية غير موجودة")

    if data.name:
        current_user.name = data.name

    return ProfileUpdateResponse(
        name=current_user.name,
        bio=profile.bio,
        has_picture=True if profile.profile_picture_data else False
    )


@router.post(
    "/profile/picture",
    dependencies=[Depends(allow_profile)]
)
@limiter.limit(HEAVY_LIMIT)
async def upload_picture(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="يجب ان يكون الملف صورة")

    image_bytes = await file.read()

    profile = await ProfileService.update_profile_picture(
        db,
        current_user.user_id,
        image_bytes,
    )

    if not profile:
        raise HTTPException(status_code=404, detail="الصفحة الشخصية غير موجودة")

    return {"message": "تم رفع صورة الملف الشخصي بنجاح"}


@router.get("/picture/me")
@limiter.limit(HEAVY_LIMIT)
async def get_my_profile_picture(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    profile = await ProfileService.get_profile(db, current_user.user_id)

    if not profile or not profile.profile_picture_data:
        raise HTTPException(status_code=404, detail="صورة الملف الشخصي غير موجودة")

    return Response(
        content=profile.profile_picture_data,
        media_type="image/png"
    )