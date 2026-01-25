from datetime import datetime, timezone
from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List

if TYPE_CHECKING:
    from src.models.Question import Question
    from src.models.User import User
    from src.models.Question_Option import Question_Option

class Quiz_Attempt (SQLModel , table = True):
    attempt_id : int |None = Field(default=None , primary_key=True)
    student_id :int = Field(foreign_key='user.user_id', index=True ,nullable=False)
    question_id :int = Field(foreign_key='question.question_id', index=True  ,nullable=False)

    session_start : datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    session_end : datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    answer_id : int = Field(foreign_key='question_option.option_id', index=True, nullable=False)

    student : "User" = Relationship(back_populates="quiz_attempt")
    question : "Question" = Relationship(back_populates="quiz_attempt")
    answer : "Question_Option" = Relationship(back_populates="quiz_attempt")

    
