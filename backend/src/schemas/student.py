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

    
class CreateQuizSubmission(BaseModel):
    quiz_id: int
    answers: list[CreateQuestionAnswer]

class AnswerReview(BaseModel):
    question_id: int
    student_answer_id: int
    correct_answer_id: int
    is_correct: bool = False

class QuizReviewResponse(BaseModel):
    status: str
    message: str
    results: list[AnswerReview]