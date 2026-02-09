from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  
if TYPE_CHECKING:

    from src.models.Quiz_Attempt import Quiz_Attempt
    from src.models.Question import Question

class Question_Option(SQLModel , table= True):
    option_id : int |None = Field(default=None , primary_key=True)
    question_id :int = Field(foreign_key='question.question_id', index=True , nullable=False)
    option_text:str = Field(nullable=False)
    is_correct : bool = Field(nullable=False)

    question : "Question" = Relationship(back_populates="question_option")
    quiz_attempt :list["Quiz_Attempt"] = Relationship(back_populates="answer")
