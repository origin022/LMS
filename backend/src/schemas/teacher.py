from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    name: str
    class_id: int




class LectureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int

class MediaRead(BaseModel):
    media_id: int
    file_path: str
    file_name: str
    mime_type: str
    created_at: datetime

class CourseMin(BaseModel):
    name: str

class LectureSimple(BaseModel):
    lecture_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    course: Optional[CourseMin] 
    model_config = ConfigDict(from_attributes=True)

class LectureRead(BaseModel):
    lecture_id: int
    title: str
    description: Optional[str]
    course_id: int
    created_at: datetime
    text: Optional[str] = None
    media: list[MediaRead] = []






class QuizRead(BaseModel):
    quiz_id: int
    title: str
    description: Optional[str]
    lecture_id: int
    question: List["QuestionRead"] = []
    model_config = ConfigDict(from_attributes=True)




class LectureBasic (BaseModel):
    lecture_id: int
    title: str
    model_config = ConfigDict(from_attributes=True)

class CourseWithLectures(BaseModel):
    course_id: int
    lecture: List[LectureBasic]  
    model_config = ConfigDict(from_attributes=True)

class CourseBasic (BaseModel):
    course_id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class CourseRead(BaseModel):
    class_id: int
    course: List[CourseBasic] 
    model_config = ConfigDict(from_attributes=True)




class ClassroomRead(BaseModel):
    class_id: int
    class_name: str
    course :list[CourseBasic]
    
    model_config = ConfigDict(from_attributes=True)

   





class QuestionRead(BaseModel):
    question_id: int
    question_text: str
    quiz_id: int
    difficulty_level: int
    question_option: List["OptionRead"] = []
    model_config = ConfigDict(from_attributes=True)





class OptionRead(BaseModel):
    option_id: int
    option_text: str
    question_id: int
    model_config = ConfigDict(from_attributes=True)








class CourseUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = None

class LectureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[int] = None

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None

class OptionUpdate(BaseModel):
    option_test: Optional[str] = None
    is_correct: Optional[bool] = None


class AssignClassSchema(BaseModel):
    class_id: int
    user_id: int




class GeneratedOption(BaseModel):
    option_test: str
    is_correct: bool

class GeneratedQuestion(BaseModel):
    question_text: str
    difficulty: int
    tag: str
    options: List[GeneratedOption]

class GeneratedQuizResponse(BaseModel):
    questions: List[GeneratedQuestion]

class QuizGenerateRequest(BaseModel):
    lecture_id: int  
    quiz_id: int
    num_questions: int = 5