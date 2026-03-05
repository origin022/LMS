import io
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import select 
from src.schemas.admin import ClassroomRead
from src.services.admin import AdminService
from src.core.auth import PermissionChecker
from src.schemas.teacher import CourseRead, CourseWithLectures, LectureRead, LectureSimple
from src.services.teacher import TeacherService
from src.models import Media
from src.core.dep import get_session
from src.schemas.users import ReadeUserPublic
from src.services.users import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
import mimetypes

router = APIRouter(tags=["Public Users"])

@router.get("/classrooms", response_model=list[ClassroomRead])
async def get_all_classrooms(
    db: AsyncSession = Depends(get_session),
):
    return await AdminService.get_all_classrooms(db)

@router.get("/users/{user_id}", response_model=ReadeUserPublic)
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

    return ReadeUserPublic(
        user_id=user.user_id,
        name=user.name,
        bio=user.profile.bio if user.profile else "طالب في المنصة",
        profile_picture_url=pic_url 
    )

@router.get("/users/{user_id}/picture")
async def get_user_picture(
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
async def get_course_lectures(
    course_id: int,
    db: AsyncSession = Depends(get_session),
):
    return await TeacherService.get_lecture(
        db=db, 
        course_id=course_id
    )



@router.get("/courses/{class_id}",response_model=CourseRead)
async def get_full_course_details(
    class_id: int, 
    db: AsyncSession = Depends(get_session)
):
    return await TeacherService.get_course(db, class_id)
@router.get("/lectures/latest", response_model=list[LectureSimple])
async def get_recent_lectures(
    db: AsyncSession = Depends(get_session),
    limit: int = 6
):
    return await TeacherService.get_all_recent_lectures(db, limit)


@router.get("/lectures/{lecture_id}",response_model=LectureRead)
async def get_full_lecture_details(
    lecture_id: int, 
    db: AsyncSession = Depends(get_session)
):
    return await TeacherService.get_lecture_details(db, lecture_id)







