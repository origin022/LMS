from datetime import datetime, timezone
from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Classroom import Classroom
from src.models import Lecture, Media, Question, Question_Option, Quiz
from src.models.Course import Course
from sqlalchemy.orm import selectinload
from src.schemas.teacher import CourseCreate, LectureCreate, OptionCreate, OptionRead, QuestionCreate, QuizCreate, QuizRead

class TeacherService:
   
    @staticmethod
    async def create_course(db: AsyncSession, data: CourseCreate, teacher_id: int):
        new_course = Course(
            name=data.name,
            class_id=data.class_id,
            teacher_id=teacher_id
        )
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        return new_course
    
    


    @staticmethod
    async def get_teacher_courses(db: AsyncSession, teacher_id: int):
        stmt = select(Course).where(Course.teacher_id == teacher_id)
        result = await db.exec(stmt)
        return result.all()

  
    @staticmethod
    async def delete_course(db: AsyncSession, course_id: int):
        course = await TeacherService.get_course(db, course_id)
        await db.delete(course)
        await db.commit()
        return {"message": "Course deleted successfully"}




    @staticmethod
    async def create_lecture(db: AsyncSession, data: LectureCreate, teacher_id: int):
        lecture = Lecture(
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            user_id=teacher_id
        )
        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)
        return lecture


    @staticmethod
    async def delete_lecture(db: AsyncSession, lecture_id: int):
        stmt = select(Lecture).where(Lecture.lecture_id == lecture_id)
        result = await db.exec(stmt)
        lecture = result.first()
        if not lecture:
            raise HTTPException(404, "Lecture not found")

        await db.delete(lecture)
        await db.commit()
        return {"message": "Lecture deleted successfully"}






    @staticmethod
    async def create_quiz(db: AsyncSession, data: QuizCreate, current_user):
        quiz = Quiz(
            title=data.title,
            description=data.description,
            duration_minute=data.duration_minute,
            course_id=data.course_id,
            lecture_id=data.lecture_id,
            user_id=current_user.user_id
            
        )
        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)
        return quiz

    @staticmethod
    async def get_course_quizzes(db: AsyncSession, course_id: int):
        stmt = select(Quiz).where(Quiz.course_id == course_id).options(selectinload(Quiz.question))
        result = await db.exec(stmt)
        return result.all()






    @staticmethod
    async def create_question(db: AsyncSession, data: QuestionCreate):
        question = Question(
            question_text=data.question_text,
            quiz_id=data.quiz_id,
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def get_quiz_questions(db: AsyncSession, quiz_id: int , response_model=list[QuizRead]):
        stmt = select(Question).where(Question.quiz_id == quiz_id).options(
            selectinload(Question.question_option) 
        )
        result = await db.exec(stmt)
        return result.all()



    @staticmethod
    async def create_option(db: AsyncSession, data: OptionCreate):
        option = Question_Option(
            option_test=data.option_test,
            is_correct=data.is_correct,
            question_id=data.question_id
        )
        db.add(option)
        await db.commit()
        await db.refresh(option)
        return option





    @staticmethod
    async def create_media(
        db: AsyncSession,
        lecture_id: int,
        file_name: str,
        file_data: bytes,
        mime_type: str
    ):
        media = Media(
            lecture_id=lecture_id,
            file_name=file_name,
            file_data=file_data,
            mime_type=mime_type,
            created_at=datetime.now(timezone.utc)
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media
    


    @staticmethod
    async def get_course(db: AsyncSession, course_id: int):
        stmt = (
            select(Course)
            .where(Course.course_id == course_id)
            .options(
                selectinload(Course.lecture),
                selectinload(Course.quiz)
            )
        )
        result = await db.exec(stmt)
        course = result.first()
        if not course:
            raise HTTPException(404, "Course not found")
        return course

    @staticmethod
    async def get_lectur(db: AsyncSession, lecture_id: int):
        stmt = (
            select(Lecture)
            .where(Lecture.lecture_id == lecture_id)
            .options(
                selectinload(Lecture.media),    
                selectinload(Lecture.question).selectinload(Question.question_option) # جلب الأسئلة مع خياراتها!
            )
        )
        result = await db.exec(stmt)
        lecture = result.first()
        if not lecture:
            raise HTTPException(404, "Lecture not found")
        return lecture
    


    @staticmethod
    async def get_class(db: AsyncSession, class_id: int):
        stmt = (
            select(Classroom)
            .where(Classroom.class_id == class_id)
            .options(
                selectinload(Classroom.course),
            )  
        )
        result = await db.exec(stmt)
        courses = result.first()
        if not courses:
            raise HTTPException(404, "Class not found")
        return courses