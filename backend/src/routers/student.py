from src.core.dep import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException,  status, Request
from src.core.auth import PermissionChecker
from src.services.student import StudentService
from src.services.teacher import TeacherService
from src.schemas.student import  AnswerResponse, NextQuestionRequest, QuestionSubmission, RankResponse, ReadEnrollments
from src.core.security import limiter, DEFAULT_LIMIT, SENSITIVE_LIMIT

router = APIRouter(
    prefix="",
    tags=["Student"]
)

@router.get("/enrollments", status_code=status.HTTP_200_OK , response_model=list[ReadEnrollments])
@limiter.limit(DEFAULT_LIMIT)
async def get_enrollments(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view enrollments"])),
):
    return await StudentService.get_enrollments(
        db=db,
        student_id=current_user.user_id
    )


@router.get("/courses/{course_id}/lectures/quiz-map")
@limiter.limit(DEFAULT_LIMIT)
async def get_quiz_map(request: Request, course_id: int, db: AsyncSession = Depends(get_session)):
    return await TeacherService.get_lectures_quiz_map(db, course_id)


@router.post("/enrollments/trigger/{course_id}", status_code=status.HTTP_200_OK)
@limiter.limit(SENSITIVE_LIMIT)
async def trigger_automatic_enrollment(
    request: Request,
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view enrollments"]))
):
    enrollment = await StudentService.ensure_enrollment(
        db=db,
        course_id=course_id,
        student_id=current_user.user_id
    )
    
    return enrollment





@router.delete("/enrollments/{course_id}")
@limiter.limit(SENSITIVE_LIMIT)
async def unenroll_from_course(
    request: Request,
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view enrollments"]))
):
    deleted = await StudentService.delete_enrollment(
        db=db,
        course_id=course_id,
        student_id=current_user.user_id 
    )
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    return {"message": "Unenrolled successfully"}







@router.get("/next-question/{quiz_id}", response_model=NextQuestionRequest, response_model_exclude_none=True)
@limiter.limit(DEFAULT_LIMIT)
async def get_next_question(
    request: Request,
    quiz_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Quiz attempt"]))
):
 
    return await StudentService.get_next_question(
        db=db, 
        student_id=current_user.user_id, 
        quiz_id=quiz_id
    )

@router.post("/submit-answer", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(SENSITIVE_LIMIT)
async def submit_answer(
    request: Request,
    data: QuestionSubmission,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Quiz attempt"]))
):
 
    return await StudentService.submit_answer(
        db=db,
        student_id=current_user.user_id,
        data=data
    )


@router.get("/course-rank/{course_id}", response_model=RankResponse)
@limiter.limit(DEFAULT_LIMIT)
async def get_student_course_rank(
    request: Request,
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Quiz attempt"]))
):
  
    return await StudentService.get_course_rank(
        db=db,
        student_id=current_user.user_id,
        course_id=course_id
    )