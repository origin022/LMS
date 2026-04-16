from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class OptionRead(BaseModel):
    option_id: int
    option_text: str
    is_correct: bool
    question_id: int
    model_config = ConfigDict(from_attributes=True)


class QuestionRead(BaseModel):
    question_id: int
    question_text: str
    quiz_id: int
    difficulty_level: int
    question_option: List["OptionRead"] = []
    model_config = ConfigDict(from_attributes=True)

    

class QuizRead(BaseModel):
    quiz_id: int
    title: str
    question: List["QuestionRead"] = []
    lecture_id: int
    model_config = ConfigDict(from_attributes=True)


class LectureSimple(BaseModel):
    lecture_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    lecture_image: Optional[str] = None
    media: list[MediaRead] = []
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    name: str
    class_id: Optional[int] = None

class LectureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int

class QuizCreate(BaseModel):
    title: str
    quiz_id: int
    lecture_id: int
    source: Optional[str] = "video" # "video" or "document"

class MediaRead(BaseModel):
    media_id: int
    file_path: str
    file_name: str
    mime_type: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CourseMin(BaseModel):
    name: str

class LectureRead(BaseModel):
    lecture_id: int
    title: str
    description: Optional[str]
    course_id: int
    created_at: datetime
    text: Optional[str] = None
    media: list[MediaRead] = []
    likes_count: int = 0
    is_liked: bool = False
    quiz_id: Optional[int] = None
    lecture_image: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)





class LectureBasic (BaseModel):
    lecture_id: int
    title: str
    model_config = ConfigDict(from_attributes=True)

class CourseWithLectures(BaseModel):
    course_id: int
    course_name: Optional[str] = None
    lecture: List[LectureSimple]  
    model_config = ConfigDict(from_attributes=True)

class CourseBasic (BaseModel):
    course_id: int
    name: str
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    course_thumbnail: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CourseRead(BaseModel):
    class_id: int
    course: List[CourseBasic] 
    model_config = ConfigDict(from_attributes=True)

class ClassroomRead(BaseModel):
    class_id: int
    class_name: str
    class_image: Optional[str] = None
    course :list[CourseBasic]
    model_config = ConfigDict(from_attributes=True)





class CourseUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = None

class LectureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[int] = None

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


class OptionBulkUpdate(BaseModel):
    option_id: int
    option_text: str
    is_correct: bool

class QuestionBulkUpdate(BaseModel):
    question_id: int
    question_text: str
    difficulty_level: int
    options: List[OptionBulkUpdate]

class QuizBulkUpdate(BaseModel):
    title: str
    questions: List[QuestionBulkUpdate]
