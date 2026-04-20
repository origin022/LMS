import io
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import select 
from src.schemas.admin import ClassroomRead
from src.services.admin import AdminService
from src.core.auth import PermissionChecker, get_current_user , get_current_user_optional
from src.schemas.teacher import CourseRead, CourseWithLectures, LectureRead, LectureSimple
from src.services.teacher import TeacherService
from src.models import Media, User
from src.core.dep import get_session
from src.schemas.users import ReadeUserPublic
from src.services.users import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
import mimetypes
from typing import Optional
from src.core.security import limiter, PUBLIC_LIMIT, HEAVY_LIMIT

router = APIRouter(tags=["Public Users"])

@router.get("/classrooms", response_model=list[ClassroomRead])
@limiter.limit(PUBLIC_LIMIT)
async def get_all_classrooms(
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    return await AdminService.get_all_classrooms(db)

@router.get("/users/{user_id}", response_model=ReadeUserPublic)
@limiter.limit(PUBLIC_LIMIT)
async def get_user_full_profile(
    user_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_session)
):
    user = await UserService.get_public_user_data(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    pic_url = None
    if user.profile and user.profile.profile_picture_data:
        pic_url = f"{request.base_url}api/v1/users/{user_id}/picture"

    return ReadeUserPublic(
        user_id=user.user_id,
        name=user.name,
        bio=user.profile.bio if user.profile else "طالب في المنصة",
        profile_picture_url=pic_url 
    )

@router.get("/users/{user_id}/picture")
@limiter.limit(HEAVY_LIMIT)
async def get_user_picture(
    request: Request,
    user_id: int, 
    db: AsyncSession = Depends(get_session),
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


@router.get("/users/courses/{course_id}/lectures", response_model=CourseWithLectures)
@limiter.limit(PUBLIC_LIMIT)
async def get_course_lectures(
    request: Request,
    course_id: int,
    db: AsyncSession = Depends(get_session),
):
    return await TeacherService.get_lecture(
        db=db, 
        course_id=course_id
    )



@router.get("/courses/{class_id}",response_model=CourseRead)
@limiter.limit(PUBLIC_LIMIT)
async def get_full_course_details(
    request: Request,
    class_id: int, 
    db: AsyncSession = Depends(get_session)
):
    return await TeacherService.get_course(db, class_id)
@router.get("/lectures/latest", response_model=list[LectureSimple])
@limiter.limit(PUBLIC_LIMIT)
async def get_recent_lectures(
    request: Request,
    db: AsyncSession = Depends(get_session),
    limit: int = 6
):
    return await TeacherService.get_all_recent_lectures(db, limit)


@router.get("/lectures/{lecture_id}", response_model=LectureRead)
@limiter.limit(PUBLIC_LIMIT)
async def get_full_lecture_details(
    request: Request,
    lecture_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    uid = current_user.user_id if current_user else None
    return await TeacherService.get_lecture_details(db, lecture_id,uid)







