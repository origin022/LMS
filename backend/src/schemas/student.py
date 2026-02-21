from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from src.schemas.teacher import CourseBasic


class ReadEnrollments(BaseModel):
    enrollment_id: int
    student_id: int
    course: CourseBasic
    model_config = ConfigDict(from_attributes=True)

class CreateEnrollment(BaseModel):
    course_id: int
    student_id: int

class CreateQuestionAnswer(BaseModel):
    question_id: int
    answer_id: int  




class RankResponse(BaseModel):
    student_score: int
    rank: int
    total_students: int
    message: str



class QuestionSubmission(BaseModel):
    quiz_id: int
    question_id: int
    answer_id: int



class QuestionOptionRead(BaseModel):
    option_id: int
    option_text: str

class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer_id: int
    points_earned: int
    current_streak: int
    next_difficulty: int
    message: str


class NextQuestionRequest(BaseModel):
    status: str
    quiz_id: Optional[int] = None      
    question_id: Optional[int] = None
    question_text: Optional[str] = None
    difficulty: Optional[int] = None
    options: Optional[List[QuestionOptionRead]] = None
    message: Optional[str] = None


