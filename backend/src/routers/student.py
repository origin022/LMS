from src.core.dep import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException,  status  
from src.core.auth import PermissionChecker
from src.services.student import StudentService
from src.schemas.student import  QuizReviewResponse, QuizSubmission, ViewEnrollments

router = APIRouter(
    prefix="",
    tags=["Student"]
)

@router.get("/enrollments", status_code=status.HTTP_200_OK , response_model=list[ViewEnrollments])
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



@router.post(
    "/quizzes/submit", 
    status_code=status.HTTP_201_CREATED, 
    response_model=QuizReviewResponse
)
async def submit_quiz_answers(
    submission: QuizSubmission,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Quiz attempt"])) 
):

    return await StudentService.QuestionAnswer(
        db=db,
        student_id=current_user.user_id,
        submission=submission
    )