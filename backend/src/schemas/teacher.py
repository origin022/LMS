from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, model_validator


class CourseCreate(BaseModel):
    name: str
    class_id: int




class LectureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int


class LectureRead(BaseModel):
    title: str
    description: Optional[str]
    course_id: int
    created_at: datetime
    media: List["MediaRead"] = []


class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minute: int
    course_id: Optional[int] = None
    lecture_id: Optional[int] = None
    @model_validator(mode="after")
    def check_relation(self):
        if not self.course_id and not self.lecture_id:
            raise ValueError("Quiz must belong to a course or a lecture")
        if self.course_id and self.lecture_id:
            raise ValueError("Quiz cannot belong to both course and lecture")
        return self



class QuizRead(BaseModel):
    quiz_id: int
    title: str
    description: Optional[str]
    duration_minute: int
    course_id: Optional[int] = None
    lecture_id: Optional[int] = None
    questions: List["QuestionRead"] = []


class LeactureBasic (BaseModel):
    lecture_id: int
    title: str
    class Config:
        from_attributes = True

class CourseRead(BaseModel):
    course_id: int
    name: str
    class_id: int
    teacher_id: int
    lecture: List[LeactureBasic] = []
    quiz: List[QuizRead] = []

class CourseBasic (BaseModel):
    course_id: int
    name: str
    class Config:
        from_attributes = True
class classread(BaseModel):
    class_id: int
    class_name: str
    course :list[CourseBasic]
    class Config:
        from_attributes = True
   

class QuestionCreate(BaseModel):
    question_text: str
    quiz_id: int



class QuestionRead(BaseModel):
    question_id: int
    question_text: str
    quiz_id: int
    question_option: List["OptionRead"] = []
    class Config:
        from_attributes = True


class OptionCreate(BaseModel):
    option_test: str
    is_correct: bool
    question_id: int


class OptionRead(BaseModel):
    option_id: int
    option_test: str
    question_id: int
    class Config:
        from_attributes = True



class MediaCreate(BaseModel):
    lecture_id: int


class MediaRead(BaseModel):
    media_id: int
    lecture_id: int
    file_name: str
    mime_type: str
    created_at: datetime

