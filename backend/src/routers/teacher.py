from fastapi import APIRouter, Depends,  status  
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.auth import PermissionChecker
from src.core.dep import get_session
from src.services.teacher import TeacherService
from src.schemas.teacher import (
    CourseCreate,
    LectureCreate,
    QuestionRead,
    QuizCreate,
    QuestionCreate,
    OptionCreate,
    QuizRead,
    
)

router = APIRouter(
    prefix="",
    tags=["Teacher"]
)



@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"])),


):
    return await TeacherService.create_course(
        db=db,
        data=data,
        teacher_id=current_user.user_id
    )



@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"]))
):
    return await TeacherService.delete_course(
        db=db,
        course_id=course_id
        )




@router.post("/lectures", status_code=status.HTTP_201_CREATED)
async def create_lecture(
    data: LectureCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.create_lecture(
        db=db,
        data=data,
        teacher_id=current_user.user_id
    )


@router.get("/courses/{course_id}/lectures")
async def get_course_lectures(
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.get_course_lectures(
        db=db, 
        course_id=course_id
    )


@router.delete("/lectures/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lecture(
    lecture_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.delete_lecture(
        db=db,
        lecture_id=lecture_id
    )




@router.post("/quizzes", status_code=status.HTTP_201_CREATED)
async def create_quiz(
    data: QuizCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.create_quiz(
        db=db,
        data=data,
        current_user=current_user
    )


@router.get("/courses/{course_id}/quizzes",response_model=list[QuizRead])
async def get_course_quizzes(
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz","Attempt Quiz"]))
):
    return await TeacherService.get_course_quizzes(
        db=db, 
        course_id=course_id
    )


@router.post("/questions", status_code=status.HTTP_201_CREATED)
async def create_question(
    data: QuestionCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.create_question(
        db=db, 
        data=data)


@router.get("/quizzes/{quiz_id}/questions",response_model=list[QuestionRead])
async def get_quiz_questions(
    quiz_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.get_quiz_questions(
        db=db, 
        quiz_id=quiz_id)


@router.post("/options", status_code=status.HTTP_201_CREATED)
async def create_option(
    data: OptionCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.create_option(
        db=db,
        data=data
    )









