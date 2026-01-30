from pydantic import BaseModel
from src.schemas.teacher import CourseBasic


class ViewEnrollments(BaseModel):
    enrollment_id: int
    student_id: int
    course: CourseBasic
    class Config:
        from_attributes = True


class QuestionAnswer(BaseModel):
    question_id: int
    answer_id: int  

    
class QuizSubmission(BaseModel):
    quiz_id: int
    answers: list[QuestionAnswer]

class AnswerReview(BaseModel):
    question_id: int
    student_answer_id: int
    correct_answer_id: int
    is_correct: bool

class QuizReviewResponse(BaseModel):
    status: str
    message: str
    results: list[AnswerReview]