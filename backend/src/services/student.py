from http.client import HTTPException
from unittest import result
from sqlmodel import select
from src.models import Question, Question_Option
from src.models.Quiz_Attempt import Quiz_Attempt
from src.models.Enrollment import Enrollment
from src.models.Course import Course
from src.schemas.student import  AnswerReview, QuizReviewResponse, ViewEnrollments , QuizSubmission
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload



class StudentService:
    @staticmethod
    async def get_enrollments(db: AsyncSession,  student_id: int ):
        stmt = (
            select(Enrollment)
            .where(Enrollment.student_id == student_id)
            .options(selectinload(Enrollment.course))
        )
        result = await db.exec(stmt)
        return result.all()

    @staticmethod
    async def ensure_enrollment(db: AsyncSession, course_id: int, student_id: int):
        course_stmt = select(Course).where(Course.course_id == course_id)
        course_result = await db.exec(course_stmt)
        course = course_result.first()
        if not course:
            return {"error": "Course not found"}

        enrollment_stmt = select(Enrollment).where(
            Enrollment.course_id == course_id,
            Enrollment.student_id == student_id
        )
        result = await db.exec(enrollment_stmt)
        existing_enrollment = result.first()
        if existing_enrollment:
            return {"message": "Student already enrolled in this course"}

        new_enrollment = Enrollment(
            course_id=course_id,
            student_id=student_id
        )
        db.add(new_enrollment)
        await db.commit()
        await db.refresh(new_enrollment)
        return new_enrollment

    @staticmethod
    async def delete_enrollment(db: AsyncSession, course_id: int, student_id: int):
        statement = select(Enrollment).where(
            Enrollment.course_id == course_id,
            Enrollment.student_id == student_id
        )

        result = await db.exec(statement)
        enrollment = result.first()
        if enrollment:
            await db.delete(enrollment)
            await db.commit()
            return True

        return False

    @staticmethod
    async def QuestionAnswer(db: AsyncSession, student_id: int, submission: QuizSubmission):
        check_stmt = select(Quiz_Attempt).where(
            Quiz_Attempt.student_id == student_id,
            Quiz_Attempt.quiz_id == submission.quiz_id
        )
        existing = (await db.exec(check_stmt)).first()
        if existing:
            raise HTTPException(status_code=400, detail="لقد أتممت هذا الكوز مسبقاً.")
        correct_options_stmt = select(Question_Option).join(Question).where(
            Question.quiz_id == submission.quiz_id,
            Question_Option.is_correct == True
        )
        result = await db.exec(correct_options_stmt)
        all_correct = result.all()

        correct_map = {opt.question_id: opt.option_id for opt in all_correct}

        review_list = []

        for ans in submission.answers:
            new_attempt = Quiz_Attempt(
                student_id=student_id,
                quiz_id=submission.quiz_id,
                question_id=ans.question_id,
                answer_id=ans.answer_id
            )
            db.add(new_attempt)
            correct_id = correct_map.get(ans.question_id)

            review_list.append(AnswerReview(
                question_id=ans.question_id,
                student_answer_id=ans.answer_id,
                correct_answer_id=correct_id,
                is_correct=(ans.answer_id == correct_id)
            )
            )

        await db.commit()
        return QuizReviewResponse(
            status="success",
            message="تم حفظ الإجابات، إليك المراجعة",
            results=review_list
    )