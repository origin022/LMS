from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile,  status ,File
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.auth import PermissionChecker
from src.core.dep import get_session
from src.services.teacher import TeacherService
from src.schemas.teacher import (
    CourseBasic,
    CourseCreate,
    LectureCreate,
    LectureRead,
    QuizRead,
    CourseUpdate,      
    LectureUpdate,     
    AssignClassSchema,
    LectureSimple,
    QuizCreate,
    QuizBulkUpdate
)

router = APIRouter(
    prefix="",
    tags=["Teacher"]
)



@router.post("/teacher/courses",  response_model=CourseBasic)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"])),


):
    return await TeacherService.create_course(
        db=db,
        data=data,
        user_id=current_user.user_id
    )



@router.get("/teacher/courses", response_model=list[CourseBasic])
async def get_teacher_courses(
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"]))
):
    return await TeacherService.get_teacher_courses(db, current_user.user_id)


@router.delete("/teacher/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"]))
):
    return await TeacherService.delete_course(
        db=db,
        course_id=course_id,
        current_user=current_user
        )




@router.post("/teacher/courses/{course_id}/lectures", status_code=status.HTTP_201_CREATED, response_model=LectureRead)
async def create_lecture(
    data: LectureCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.create_lecture(
        db=db,
        data=data,
        current_user=current_user
    )





@router.delete("/lectures/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lecture(
    lecture_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.delete_lecture(
        db=db,
        lecture_id=lecture_id,
        current_user=current_user
    )











@router.get("/quizzes/{quiz_id}/questions",response_model=QuizRead)
async def get_quiz_questions(
    quiz_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    quiz = await TeacherService.get_quiz_questions(db, quiz_id)
    return quiz



@router.patch("/courses/{course_id}", response_model=CourseBasic)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"]))
):
    return await TeacherService.update_course(
        db=db,
        course_id=course_id,
        data=data,
        current_user=current_user
    )

@router.patch("/lectures/{lecture_id}", response_model=LectureUpdate)
async def update_lecture(
    lecture_id: int,
    data: LectureUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.update_lecture(
        db=db,
        lecture_id=lecture_id,
        data=data,
        current_user=current_user
    )


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.delete_quiz(
        db=db,
        quiz_id=quiz_id,
        current_user=current_user
    )




@router.post("/complete-teacher-setup")
async def complete_teacher_setup(
    data: AssignClassSchema,
    db: AsyncSession = Depends(get_session)
):
    return await TeacherService.assign_teacher_to_class(
        user_id=data.user_id, 
        class_id=data.class_id, 
        db=db
    )






@router.post("/lectures/{lecture_id}/upload-video",status_code=status.HTTP_201_CREATED,)
async def upload_lecture_video(
    lecture_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    media_record = await TeacherService.upload_lecture_video(
        db=db, 
        lecture_id=lecture_id, 
        file=file,
        current_user=current_user
    )
    background_tasks.add_task(
    TeacherService.process_video_transcription,
    lecture_id,
    f"/app/{media_record.file_path}"
    )

    return {"message": "الفديو تم رفعه بنجاح."}


@router.post("/generate-ai", status_code=status.HTTP_201_CREATED)
async def generate_quiz_by_ai(
    data: QuizCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
  
    try:
        result = await TeacherService.generate_and_save_quiz(session, data, current_user.user_id)
        return result
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ أثناء توليد الكويز: {str(e)}"
        )

@router.patch("/quizzes/{quiz_id}/bulk")
async def bulk_update_quiz(
    quiz_id: int,
    data: QuizBulkUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.bulk_update_quiz(
        db=db,
        quiz_id=quiz_id,
        data=data,
        current_user=current_user
    )


@router.patch("/teacher/courses/{course_id}/thumbnail", status_code=status.HTTP_200_OK)
async def update_course_thumbnail(
    course_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["manage corse"]))
):
    return await TeacherService.upload_course_thumbnail(db, course_id, file, current_user)

@router.patch("/teacher/lectures/{lecture_id}/thumbnail", status_code=status.HTTP_200_OK)
async def update_lecture_thumbnail(
    lecture_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Publish"]))
):
    return await TeacherService.upload_lecture_image(db, lecture_id, file, current_user)