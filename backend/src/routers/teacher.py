from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile,  status ,File
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.auth import PermissionChecker
from src.core.dep import get_session
from src.services.teacher import TeacherService
from src.schemas.teacher import (
    CourseBasic,
    CourseCreate,
    LectureCreate,
    LectureRead,
    QuestionRead,
    QuizCreate,
    QuestionCreate,
    OptionCreate,
    QuizRead,
    CourseUpdate,      
    LectureUpdate,     
    QuizUpdate,
    QuestionUpdate,
    OptionUpdate,
    AssignClassSchema
    
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
        user_id=current_user.user_id
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




@router.post("/teacher/lectures/{lecture_id}/quizzes", status_code=status.HTTP_201_CREATED)
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





@router.post("/questions", status_code=status.HTTP_201_CREATED)
async def create_question(
    data: QuestionCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.create_question(
        db=db, 
        data=data)


@router.get("/quizzes/{quiz_id}/questions",response_model=QuizRead)
async def get_quiz_questions(
    quiz_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    quiz = await TeacherService.get_quiz_questions(db, quiz_id)
    return quiz

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

@router.patch("/lectures/{lecture_id}", response_model=LectureRead)
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

@router.patch("/quizzes/{quiz_id}", response_model=QuizUpdate)
async def update_quiz(
    quiz_id: int,
    data: QuizUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.update_quiz(
        db=db,
        quiz_id=quiz_id,
        data=data,
        current_user=current_user
    )

@router.patch("/questions/{question_id}", response_model=QuestionUpdate)
async def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.update_question(
        db=db,
        question_id=question_id,
        data=data,
        current_user=current_user
    )

@router.patch("/options/{option_id}",                                                        response_model=OptionUpdate)
async def update_option(
    option_id: int,
    data: OptionUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Assign Quiz"]))
):
    return await TeacherService.update_option(
        db=db,
        option_id=option_id,
        data=data,
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
        media_record.file_path  
    )

    return {"message": "الفديو تم رفعه بنجاح."}
