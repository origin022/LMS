import json
import os
from groq import Groq
import shutil
from src.core.dep import engine
import uuid
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Like import Like
from src.models.Media import Media
from src.core.security import get_owned_obj
from src.models.User import User
from src.models import Teacher_Assignment
from src.models.Lecture import Lecture
from src.models.Quiz import Quiz
from src.models.Question import Question
from src.models.Question_Option import Question_Option
from src.models.Course import Course
from sqlalchemy.orm import joinedload, selectinload
from src.schemas.teacher import (
    CourseCreate, CourseUpdate, LectureCreate, LectureUpdate, 
    LectureRead, MediaRead, QuizCreate,
    QuizBulkUpdate
)
from sqlalchemy import func
from src.core.config import config
import anyio
from typing import Optional

groq_client = Groq(api_key=config.GROQ_API_KEY)

class TeacherService:
   
    @staticmethod
    async def create_course(db: AsyncSession, data: CourseCreate, user_id: int):
        statement = select(Teacher_Assignment).where(Teacher_Assignment.user_id == user_id)
        result = await db.exec(statement)
        assignment = result.first()

        if not assignment:
            raise HTTPException(
                status_code=403, 
                detail="يجب أن تكون مرتبطاً بكلاس أولاً لإنشاء كورس"
            )

        new_course = Course(
            name=data.name,
            class_id=assignment.class_id,
            user_id=user_id
        )
    
        db.add(new_course)
        try:
            await db.commit()
            await db.refresh(new_course)
            return new_course
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="فشل في حفظ البيانات")
    


    @staticmethod
    async def get_teacher_courses(db: AsyncSession, user_id: int):
        stmt = select(Course).where(Course.user_id == user_id)
        result = await db.exec(stmt)
        return result.all()

  
    @staticmethod
    async def delete_course(db: AsyncSession, course_id: int, current_user: User):
        course = await get_owned_obj(db, Course, course_id, current_user, user_field="user_id")
        await db.delete(course)
        await db.commit()
        return {"message": "Course deleted successfully"}




    @staticmethod
    async def create_lecture(db: AsyncSession, data: LectureCreate, current_user: User):

        await get_owned_obj(db, Course, data.course_id, current_user)

        lecture = Lecture(
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            user_id=current_user.user_id
        )

        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)

        stmt = (
            select(Lecture)
            .where(Lecture.lecture_id == lecture.lecture_id)
            .options(selectinload(Lecture.media))
        )

        result = await db.exec(stmt)
        return result.first()




    @staticmethod
    async def delete_quiz(db: AsyncSession, quiz_id: int, current_user: User):
        quiz = await get_owned_obj(db, Quiz, quiz_id, current_user, user_field="user_id")
        await db.delete(quiz)
        await db.commit()
        return {"message": "Quiz deleted successfully"}

    @staticmethod
    async def delete_lecture(db: AsyncSession, lecture_id: int, current_user: User):
        lecture = await get_owned_obj(db, Lecture, lecture_id, current_user)
    
        await db.delete(lecture)
        await db.commit()
        return {"message": "Lecture deleted successfully"}
   



    @staticmethod
    async def get_quiz_questions(db: AsyncSession, quiz_id: int):
        stmt = (
            select(Quiz)
            .where(Quiz.quiz_id == quiz_id)
            .options(
                selectinload(Quiz.question)
                .selectinload(Question.question_option)
            )
        )

        result = await db.exec(stmt)
        quiz = result.first()

        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return quiz



    

    @staticmethod
    async def get_course(db: AsyncSession, class_id: int):
        statement = select(Course).where(Course.class_id == class_id).options(selectinload(Course.user))
        result = await db.exec(statement)
        courses_list = result.all()

        if not courses_list:
            raise HTTPException(status_code=404, detail="No courses found for this class")

        courses_data = []
        for c in courses_list:
            courses_data.append({
                "course_id": c.course_id,
                "name": c.name,
                "teacher_id": c.user_id,
                "teacher_name": c.user.name if c.user else "غير معروف"
            })

        return {
            "class_id": class_id,
            "course": courses_data
        }

    @staticmethod
    async def get_lecture(db: AsyncSession, course_id: int):
        stmt_course = select(Course).where(Course.course_id == course_id)
        res_course = await db.exec(stmt_course)
        course = res_course.first()
    
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        stmt_lectures = (
            select(Lecture)
            .where(Lecture.course_id == course_id)
            .options(
                selectinload(Lecture.course),
                selectinload(Lecture.quiz).selectinload(Quiz.question).selectinload(Question.question_option)
            )
        )
        result = await db.exec(stmt_lectures)
        lectures = result.all()
    
        return {
            "course_id": course.course_id,
            "course_name": course.name,
            "lecture": lectures
        }
    



    @staticmethod
    async def get_lecture_details(db: AsyncSession, lecture_id: int, user_id: Optional[int] = None):
        stmt = select(Lecture).where(Lecture.lecture_id == lecture_id).options(
            selectinload(Lecture.media),
            selectinload(Lecture.quiz).selectinload(Quiz.question).selectinload(Question.question_option)
        )
        result = await db.exec(stmt)
        lecture = result.first()

        if not lecture:
            raise HTTPException(404, "Lecture not found")

        is_liked = False
        if user_id:
            like_stmt = select(Like).where(Like.lecture_id == lecture_id, Like.user_id == user_id)
            like_res = await db.exec(like_stmt)
            is_liked = like_res.first() is not None

        likes_count_stmt = select(func.count()).where(Like.lecture_id == lecture_id)
        likes_count_res = await db.exec(likes_count_stmt)
        likes_count = likes_count_res.one()

        quiz_id = None
        if lecture.quiz and len(lecture.quiz) > 0:
            quiz_id = lecture.quiz[0].quiz_id

        return LectureRead(
            lecture_id=lecture.lecture_id,
            title=lecture.title,
            description=lecture.description,
            course_id=lecture.course_id,
            created_at=lecture.created_at,
            text=lecture.text,
            likes_count=likes_count,
            is_liked=is_liked,
            quiz=lecture.quiz,
            quiz_id=quiz_id,
            media=[
                MediaRead.model_validate(m)
                for m in (lecture.media or [])
            ]
        )

    
    @staticmethod
    async def assign_teacher_to_class(user_id: int, class_id: int, db: AsyncSession):
        assignment = Teacher_Assignment(
            user_id=user_id,
            class_id=class_id
        )
    
        try:
            db.add(assignment)
            await db.commit()
            await db.refresh(assignment) 
        
            return {
                "status": "success",
                "message": "تم إكمال إعداد حساب الأستاذ بنجاح",
                "data": {"user_id": user_id, "class_id": class_id}
        }
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=400, 
            detail="هذا الأستاذ مرتبط بصف بالفعل أو البيانات غير صحيحة"
                )



    @staticmethod
    async def _update_entity(db: AsyncSession, model, entity_id: int, data, id_field: str):
        statement = select(model).where(getattr(model, id_field) == entity_id)
        result = await db.exec(statement)
        db_item = result.first()

        if not db_item:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def update_course(db: AsyncSession, course_id: int, data: CourseUpdate , current_user: User):
        db_course = await get_owned_obj(db, Course, course_id, current_user)
        return await TeacherService._update_entity(db, Course, course_id, data, "course_id")

    @staticmethod
    async def update_lecture(db: AsyncSession, lecture_id: int, data: LectureUpdate , current_user: User):
        db_lecture = await get_owned_obj(db, Lecture, lecture_id, current_user)
        return await TeacherService._update_entity(db, Lecture, lecture_id, data, "lecture_id")

   

    @staticmethod
    async def process_video_transcription(lecture_id: int, file_path: str):
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                return

            def sync_transcribe():
                with open(abs_path, "rb") as file:
                    return groq_client.audio.transcriptions.create(
                        file=(os.path.basename(abs_path), file.read()),
                        model="whisper-large-v3",
                        language="ar",
                        response_format="verbose_json", 
                    )

            transcribed_data = await anyio.to_thread.run_sync(sync_transcribe)

            async with AsyncSession(engine) as db:
                statement = select(Lecture).where(Lecture.lecture_id == lecture_id)
                res = await db.exec(statement)
                lecture = res.first()
            
                if lecture:
                    subtitles = []
                    if hasattr(transcribed_data, 'segments'):
                        for segment in transcribed_data.segments:
                            subtitles.append({
                                "start": segment['start'],
                                "end": segment['end'],
                                "text": segment['text']
                            })
                
                    lecture.text = json.dumps(subtitles, ensure_ascii=False)
                    await db.commit()
                    print(f"✅ تم تحديث الترجمة المتزامنة للمحاضرة {lecture_id}")

        except Exception as e:
            print(f"❌ خطأ معالجة الصوت: {str(e)}")



    @staticmethod
    async def upload_lecture_video(db: AsyncSession, lecture_id: int, file: UploadFile, current_user: User):

        statement = select(Lecture).where(Lecture.lecture_id == lecture_id)
        result = await db.exec(statement)
        db_lecture = result.first()

        if not db_lecture:
            raise HTTPException(status_code=404, detail="المحاضرة غير موجودة")

        await get_owned_obj(db, Course, db_lecture.course_id, current_user)
        
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="الملف المرفوع يجب أن يكون فيديو فقط")

        upload_dir = "/app/media/lectures"
        os.makedirs(upload_dir, exist_ok=True) 

        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        full_path = os.path.join(upload_dir, unique_name)
        file_path_relative = os.path.join("media", "lectures", unique_name).replace("\\", "/")

        try:
            def save_file():
                with open(full_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            await anyio.to_thread.run_sync(save_file)
            print(f"✅ تم حفظ الملف في: {full_path}")
        except Exception as e:
            print(f"❌ فشل حفظ الملف: {str(e)}")
            raise HTTPException(status_code=500, detail=f"فشل حفظ الملف: {str(e)}")

        new_media = Media(
            lecture_id=lecture_id,
            file_path=file_path_relative,
            file_name=file.filename, 
            mime_type=file.content_type
        )
        
        db.add(new_media)
        await db.commit()
        await db.refresh(new_media)
        
        return new_media
    



    @staticmethod
    async def generate_and_save_quiz(session: AsyncSession, data: QuizCreate, user_id: int):
        statement = select(Lecture).where(Lecture.lecture_id == data.lecture_id)
        result = await session.exec(statement)
        lecture = result.first()

        if not lecture or not lecture.text:
            raise HTTPException(status_code=404, detail="المحاضرة غير موجودة أو لم تتم معالجتها بعد")

        # Check if lecture already has a quiz
        await session.refresh(lecture, ["quiz"])
        if lecture.quiz and len(lecture.quiz) > 0:
            raise HTTPException(status_code=400, detail="هذه المحاضرة لديها كويز بالفعل")

        # Create Quiz record if quiz_id is missing
        target_quiz_id = data.quiz_id
        if not target_quiz_id:
            new_quiz = Quiz(
                title=data.title or f"اختبار ذكاء اصطناعي: {lecture.title}",
                lecture_id=lecture.lecture_id,
                user_id=user_id
            )
            session.add(new_quiz)
            await session.flush()
            await session.refresh(new_quiz)
            target_quiz_id = new_quiz.quiz_id

        # Extract plain text from JSON subtitles if necessary
        content_text = lecture.text
        try:
            parsed_data = json.loads(lecture.text)
            if isinstance(parsed_data, list):
                content_text = " ".join([item.get('text', '') for item in parsed_data if isinstance(item, dict)])
            elif isinstance(parsed_data, dict) and "segments" in parsed_data:
                content_text = " ".join([item.get('text', '') for item in parsed_data["segments"] if isinstance(item, dict)])
        except (json.JSONDecodeError, TypeError):
            # If not valid JSON, use original text as is
            pass

        if not content_text or len(content_text.strip()) < 10:
             raise HTTPException(status_code=400, detail="محتوى المحاضرة غير كافٍ لتوليد كويز")

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert educator. Generate exactly 15 MCQ questions from the text provided. "
                            "Distribution: 5 Easy (Level 1), 5 Medium (Level 2), 5 Hard (Level 3). "
                            "Each question must have exactly 4 options. "
                            "Return ONLY a JSON object with this exact structure: "
                            "{\"questions\": [{\"question_text\": \"string\", \"difficulty\": 1, \"tag\": \"string\", "
                            "\"options\": [{\"option_text\": \"string\", \"is_correct\": bool}]}]}"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Text: {content_text}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )

            raw_data = json.loads(completion.choices[0].message.content)

            for q_item in raw_data.get('questions', []):
                q_text = q_item.get('question_text') or q_item.get('text')
                
                if not q_text:
                    continue

                new_q = Question(
                    question_text=q_text,
                    quiz_id=target_quiz_id,
                    difficulty_level=int(q_item.get('difficulty', 1)),
                    concept_tags=q_item.get('tag', 'General')
                )
                session.add(new_q)
                await session.flush() 

                for opt in q_item.get('options', []):
                    o_text = opt.get('option_text')
                    
                    if not o_text:
                        continue 
                    
                    new_opt = Question_Option(
                        question_id=new_q.question_id,
                        option_text=o_text, 
                        is_correct=opt.get('is_correct', False)
                    )
                    session.add(new_opt)

            await session.commit()
            return {"status": "success", "message": "تم توليد 15 سؤالاً وحفظ الخيارات بنجاح"}

        except Exception as e:
            await session.rollback()
            print(f"GROQ ERROR: {str(e)}")
            raise HTTPException(status_code=500, detail=f"فشل التوليد: {str(e)}")
        



    @staticmethod
    async def get_all_recent_lectures(db: AsyncSession, limit_val: int): # غيرت الاسم لـ limit_val لتجنب تضارب المكتبات
        statement = (
            select(Lecture)
            .options(
                selectinload(Lecture.course),
                selectinload(Lecture.quiz).selectinload(Quiz.question).selectinload(Question.question_option)
            )
            .order_by(Lecture.lecture_id.desc())
            .limit(limit_val)
        )
        result = await db.exec(statement)
        return result.all()

    @staticmethod
    async def bulk_update_quiz(db: AsyncSession, quiz_id: int, data: QuizBulkUpdate, current_user: User):
        easy_count = sum(1 for q in data.questions if q.difficulty_level == 1)
        medium_count = sum(1 for q in data.questions if q.difficulty_level == 2)
        hard_count = sum(1 for q in data.questions if q.difficulty_level == 3)
        total_count = len(data.questions)

        if total_count != 15:
            raise HTTPException(status_code=400, detail="يجب أن يكون العدد الكلي للأسئلة 15 سؤالاً")

        if easy_count > 7 or medium_count > 7 or hard_count > 7:
            raise HTTPException(status_code=400, detail="لا يمكن تجاوز 7 أسئلة في المستوى الواحد لضمان التوازن")
        stmt = (
            select(Quiz)
            .where(Quiz.quiz_id == quiz_id, Quiz.user_id == current_user.user_id)
            .options(selectinload(Quiz.question).selectinload(Question.question_option))
        )
        res = await db.exec(stmt)
        quiz = res.first()

        if not quiz:
            raise HTTPException(status_code=404, detail="الكويز غير موجود")

        quiz.title = data.title

        current_questions = {q.question_id: q for q in quiz.question}
        input_question_ids = {q.question_id for q in data.questions if q.question_id}

        for q_id, q_obj in current_questions.items():
            if q_id not in input_question_ids:
                await db.delete(q_obj)

        for q_data in data.questions:
            if q_data.question_id in current_questions:
                question = current_questions[q_data.question_id]
                question.question_text = q_data.question_text
                question.difficulty_level = q_data.difficulty_level
            
                current_options = {o.option_id: o for o in question.question_option}
                input_option_ids = {o.option_id for o in q_data.options if o.option_id}

                for o_id, o_obj in current_options.items():
                    if o_id not in input_option_ids:
                        await db.delete(o_obj)

                for o_data in q_data.options:
                    if o_data.option_id in current_options:
                        option = current_options[o_data.option_id]
                        option.option_text = o_data.option_text
                        option.is_correct = o_data.is_correct

        try:
            await db.commit()
            return {"status": "success", "message": "تم تحديث الكويز وكافة متعلقاته بنجاح"}
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"خطأ في الحفظ: {str(e)}")