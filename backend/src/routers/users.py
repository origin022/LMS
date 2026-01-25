from fastapi import APIRouter, Depends, HTTPException, Request, Response 
from src.core.dep import get_session
from src.schemas.users import UserPublic
from src.services.users import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
import mimetypes

router = APIRouter(tags=["Public Users"])

@router.get("/{user_id}", response_model=UserPublic)
async def get_user_full_profile(
    user_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_session)
):
    user = await UserService.get_public_user_data(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    pic_url = None
    if user.profile and user.profile.profile_picture_data:
        pic_url = f"{request.base_url}api/v1/users/picture/{user_id}"

    return UserPublic(
        user_id=user.user_id,
        name=user.name,
        bio=user.profile.bio if user.profile else "طالب في المنصة",
        profile_picture_url=pic_url 
    )

@router.get("/picture/{user_id}")
async def get_user_picture(
    user_id: int, 
    db: AsyncSession = Depends(get_session)
):
    user = await UserService.get_public_user_data(db, user_id)
    
    if not user or not user.profile or not user.profile.profile_picture_data:
        raise HTTPException(status_code=404, detail="صورة الملف الشخصي غير موجودة")

    
    mime_type, _ = mimetypes.guess_type(f"user_pic.{user_id}") 
    
    if not mime_type:
        mime_type = "image/jpeg" 

    return Response(
        content=user.profile.profile_picture_data, 
        media_type=mime_type  
    )