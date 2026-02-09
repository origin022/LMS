from src.core.dep import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException,  status  
from src.core.auth import PermissionChecker
from src.services.student import StudentService
from src.schemas.student import  AnswerResponse, NextQuestionRequest, QuestionSubmission, RankResponse, ReadEnrollments

router = APIRouter(
    prefix="",
    tags=["Student"]
)

@router.get("/enrollments", status_code=status.HTTP_200_OK , response_model=list[ReadEnrollments])
async def get_enrollments(
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view enrollments"])),
):
    return await StudentService.get_enrollments(
        db=db,
        student_id=current_user.user_id
    )


@router.post("/enrollments/trigger/{course_id}", status_code=status.HTTP_200_OK)
async def trigger_automatic_enrollment(
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
async def unenroll_from_course(
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
async def get_next_question(
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
async def submit_answer(
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
async def get_student_course_rank(
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Quiz attempt"]))
):
  
    return await StudentService.get_course_rank(
        db=db,
        student_id=current_user.user_id,
        course_id=course_id
    )