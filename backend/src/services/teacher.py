import json
import os
import torch
from groq import Groq
import whisper
import shutil
from src.core.dep import engine
import uuid
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Media import Media
from src.core.security import get_owned_obj
from src.models.User import User
from src.models import Teacher_Assignment
from src.models.Lecture import Lecture
from src.models.Quiz import Quiz
from src.models.Question import Question
from src.models.Question_Option import Question_Option
from src.models.Course import Course
from sqlalchemy.orm import selectinload
from src.schemas.teacher import CourseCreate, CourseUpdate, LectureCreate, LectureUpdate, OptionUpdate, QuestionUpdate, QuizGenerateRequest, QuizUpdate
from src.core.config import config

groq_client = Groq(api_key=config.GROQ_API_KEY)

class TeacherService:
   
    @staticmethod
    async def create_course(db: AsyncSession, data: CourseCreate, user_id: int):
        check_stmt = select(Teacher_Assignment).where(
            Teacher_Assignment.user_id == user_id,
            Teacher_Assignment.class_id == data.class_id
        )
        result = await db.exec(check_stmt)
        assignment = result.first()

        if not assignment:
            raise HTTPException(
                status_code=403, 
                detail="لا يمكنك إنشاء كورس في كلاس غير مسجل فيه"
            )

        new_course = Course(
            name=data.name,
            class_id=data.class_id,
            user_id=user_id
        )   
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        return new_course
    
    


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
    async def create_lecture(db: AsyncSession, data: LectureCreate, user_id: int):
        lecture = await get_owned_obj(db, Course, data.course_id, user_id)
        lecture = Lecture(
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            user_id=user_id
        )
        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)
        return lecture


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
        statement = select(Course).where(Course.class_id == class_id)
        result = await db.exec(statement)
        courses_list = result.all()

        if not courses_list:
            raise HTTPException(status_code=404, detail="No courses found for this class")

        return {
            "class_id": class_id,
            "course": courses_list
              }

    @staticmethod
    async def get_lecture(db: AsyncSession, course_id: int):
        stmt = (
            select(Lecture)
            .where(Lecture.course_id == course_id)
            
        )
        result = await db.exec(stmt)
        lecture = result.all()
        if not lecture:
            raise HTTPException(404, "Lecture not found")
        return {
            "course_id": course_id,
            "lecture": lecture
        }
    


    @staticmethod
    async def get_lecture_details(db: AsyncSession, lecture_id: int):
        stmt = (
            select(Lecture)
            .where(Lecture.lecture_id == lecture_id)
            .options(selectinload(Lecture.media)) 
    )
        result = await db.exec(stmt)
        lecture = result.first()
        if not lecture:
            raise HTTPException(404, "Lecture not found")
        return lecture
    

    


    
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
    async def update_quiz(db: AsyncSession, quiz_id: int, data: QuizUpdate, current_user: User):
        db_quiz = await get_owned_obj(db, Quiz, quiz_id, current_user)
        return await TeacherService._update_entity(db, Quiz, quiz_id, data, "quiz_id")

    @staticmethod
    async def update_question(db: AsyncSession, question_id: int, data: QuestionUpdate, current_user: User):
        result = await db.exec(select(Question).where(Question.question_id == question_id))
        db_question = result.first()

        if not db_question:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")

        await get_owned_obj(db, Quiz, db_question.quiz_id, current_user)

        return await TeacherService._update_entity(db, Question, question_id, data, "question_id")
    @staticmethod
    async def update_option(db: AsyncSession, option_id: int, data: OptionUpdate, current_user: User):
        stmt = (
            select(Question_Option)
            .join(Question_Option.question) 
            .join(Question.quiz)          
            .where(Question_Option.option_id == option_id)
            .where(Quiz.user_id == current_user.user_id)
        )
    
        result = await db.exec(stmt)
        db_option = result.first()

        if not db_option:
            raise HTTPException(status_code=403, detail=" ليس لديك إذن لتعديل هذا الخيار أو الخيار غير موجود")

        return await TeacherService._update_entity(db, Question_Option, option_id, data, "option_id")
    



    @staticmethod
    async def process_video_transcription(lecture_id: int, file_path: str):
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"⚙️ AI Engine is running on: {device.upper()}")
        
            abs_file_path = os.path.abspath(file_path)
        
            model = whisper.load_model("base").to(device)
        
            result = model.transcribe(
                abs_file_path, 
                language="ar", 
                fp16=(device == "cuda") 
            )
            transcribed_text = result["text"]

            async with AsyncSession(engine) as db:
                statement = select(Lecture).where(Lecture.lecture_id == lecture_id)
                res = await db.exec(statement)
                lecture = res.first()
            
                if lecture:
                    lecture.text = transcribed_text
                    await db.commit()
                    print(f"✅ تم تحديث النص للمحاضرة {lecture_id} بنجاح")

        except Exception as e:
            print(f" خطأ في عملية التحويل: {str(e)}")

    
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

        upload_dir = "media/lectures"
        os.makedirs(upload_dir, exist_ok=True) 

        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        full_path = os.path.join(upload_dir, unique_name)
        file_path = full_path.replace("\\", "/")

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"فشل حفظ الملف: {str(e)}")

        new_media = Media(
            lecture_id=lecture_id,
            file_path=file_path,
            file_name=file.filename, 
            mime_type=file.content_type
        )
        
        db.add(new_media)
        await db.commit()
        await db.refresh(new_media)
        
        return new_media
    



    @staticmethod
    async def generate_and_save_quiz(session: AsyncSession, data: QuizGenerateRequest):
        statement = select(Lecture).where(Lecture.lecture_id == data.lecture_id)
        result = await session.exec(statement)
        lecture = result.first()

        if not lecture or not lecture.text:
            raise HTTPException(status_code=404, detail="المحاضرة غير موجودة")

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
                        "content": f"Text: {lecture.text}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )

            raw_data = json.loads(completion.choices[0].message.content)

            for q_item in raw_data.get('questions', []):
                q_text = q_item.get('question_text') or q_item.get('text')
                
                if not q_text:
                    continue

                new_q = Question(
                    question_text=q_text,
                    quiz_id=data.quiz_id,
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