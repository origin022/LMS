from datetime import datetime
from fastapi import HTTPException
from sqlmodel import func, select
from src.models.Lecture import Lecture
from src.models.Quiz import Quiz
from src.models.Student_Mastery import Student_Mastery
from src.models import Question, Question_Option
from src.models.Quiz_Attempt import Quiz_Attempt
from src.models.Enrollment import Enrollment
from src.models.Course import Course
from src.schemas.student import AnswerResponse, QuestionOptionRead, QuestionSubmission, NextQuestionRequest, RankResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

class StudentService:
    @staticmethod
    async def get_enrollments(db: AsyncSession, student_id: int):
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
            raise HTTPException(status_code=400, detail="أنت مشترك بالفعل في هذا الكورس")

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
    async def submit_answer(db: AsyncSession, student_id: int, data: QuestionSubmission):

        q_stmt = select(Question.difficulty_level).where(
            Question.question_id == data.question_id
        )
        q_diff = (await db.exec(q_stmt)).first()

        opt_stmt = select(Question_Option.is_correct).where(
            Question_Option.option_id == data.answer_id
        )
        is_correct_val = (await db.exec(opt_stmt)).first()


        

        course_info_stmt = (
            select(Lecture.course_id)
            .join(Quiz, Quiz.lecture_id == Lecture.lecture_id)
            .where(Quiz.quiz_id == data.quiz_id)
        )
        course_id = (await db.exec(course_info_stmt)).first()



        if q_diff is None or is_correct_val is None or course_id is None:
            raise HTTPException(status_code=404, detail="Data not found")

        m_stmt = select(Student_Mastery).where(
            Student_Mastery.user_id == student_id,
            Student_Mastery.course_id == course_id
        )
        mastery = (await db.exec(m_stmt)).first()

        if not mastery:
            mastery = Student_Mastery(
                user_id=student_id,
                course_id=course_id,
                current_difficulty=1,
                correct_streak=0,
                mastery_score=0.0,
                last_updated=datetime.now()
            )
            db.add(mastery)
            await db.flush()

        points_earned = 0

        if is_correct_val:
            mastery.correct_streak += 1
            points_map = {1: 10, 2: 25, 3: 50}
            points_earned = points_map.get(q_diff, 10)
            mastery.mastery_score += float(points_earned)

            if mastery.correct_streak >= 2 and mastery.current_difficulty < 3:
                mastery.current_difficulty += 1
                mastery.correct_streak = 0
        else:
            mastery.correct_streak = 0
            if mastery.current_difficulty > 1:
                mastery.current_difficulty -= 1

        mastery.last_updated = datetime.now()

        new_attempt = Quiz_Attempt(
            student_id=student_id,
            quiz_id=data.quiz_id,
            question_id=data.question_id,
            answer_id=data.answer_id
        )
        db.add(new_attempt)
        db.add(mastery)

        await db.commit()
        await db.refresh(mastery)

        correct_opt_stmt = select(Question_Option.option_id).where(
            Question_Option.question_id == data.question_id,
            Question_Option.is_correct == True
        )
        correct_answer_id = (await db.exec(correct_opt_stmt)).first() or 0


        return AnswerResponse(
            is_correct=bool(is_correct_val),
            correct_answer_id=correct_answer_id,
            points_earned=points_earned,
            current_streak=mastery.correct_streak,
            next_difficulty=mastery.current_difficulty,
            message="إجابة صحيحة!" if bool(is_correct_val) else "للأسف، إجابة خاطئة"
)


    @staticmethod
    async def get_next_question(db: AsyncSession, student_id: int, quiz_id: int):
        course_stmt = (
            select(Lecture.course_id)
            .join(Quiz, Quiz.lecture_id == Lecture.lecture_id)
            .where(Quiz.quiz_id == quiz_id)
        )
        course_id = (await db.exec(course_stmt)).first()
        
        if not course_id:
            return {"status": "error", "message": "Course not found"}

        mastery_stmt = select(Student_Mastery).where(
            Student_Mastery.user_id == student_id,
            Student_Mastery.course_id == course_id
        )
        mastery = (await db.exec(mastery_stmt)).first()
        target_difficulty = mastery.current_difficulty if mastery else 1

        already_answered_stmt = select(Quiz_Attempt.question_id).where(
            Quiz_Attempt.student_id == student_id,
            Quiz_Attempt.quiz_id == quiz_id
        )
        answered_ids = (await db.exec(already_answered_stmt)).all()
        
        if len(answered_ids) >= 10:
            return {"status": "completed", "message": "لقد أنهيت الـ 10 أسئلة بنجاح!"}

        next_q_stmt = select(Question).where(
            Question.quiz_id == quiz_id,
            Question.difficulty_level == target_difficulty,
            Question.question_id.not_in(answered_ids) if answered_ids else True
        ).order_by(func.random()).limit(1)

        next_q = (await db.exec(next_q_stmt)).first()

        if not next_q:
            backup_q_stmt = select(Question).where(
                Question.quiz_id == quiz_id,
                Question.question_id.not_in(answered_ids) if answered_ids else True
            ).order_by(func.random()).limit(1)
            next_q = (await db.exec(backup_q_stmt)).first()

        if not next_q:
            return {"status": "completed", "message": " لقد أتممت جميع الأسئلة."}

        options_stmt = select(Question_Option).where(Question_Option.question_id == next_q.question_id)
        options = (await db.exec(options_stmt)).all()

        return NextQuestionRequest(
            status="ongoing",
            quiz_id=quiz_id,
            question_id=next_q.question_id,
            question_text=next_q.question_text,
            difficulty=next_q.difficulty_level,
            options=[
            QuestionOptionRead(option_id=opt.option_id, option_text=opt.option_text) 
            for opt in options
    ]
)
    



    @staticmethod
    async def get_course_rank(db: AsyncSession, student_id: int, course_id: int) -> RankResponse:
        mastery_stmt = select(Student_Mastery.mastery_score).where(
            Student_Mastery.user_id == student_id,
            Student_Mastery.course_id == course_id
        )
        score_val = (await db.exec(mastery_stmt)).first() or 0

        rank_stmt = select(func.count(Student_Mastery.user_id)).where(
            Student_Mastery.course_id == course_id,
            Student_Mastery.mastery_score > score_val
        )
        higher_count = (await db.exec(rank_stmt)).first() or 0
        current_rank = higher_count + 1

        total_stmt = select(func.count(Student_Mastery.user_id)).where(
            Student_Mastery.course_id == course_id
        )
        total_count = (await db.exec(total_stmt)).first() or 1

        msg = f"أنت بالمركز الـ {current_rank} من أصل {total_count} طالب!"
        if current_rank == 1:
            msg = "أنت المتصدر حالياً "

        return RankResponse(
            student_score=int(score_val), 
            rank=current_rank,
            total_students=total_count,
            message=msg
    )