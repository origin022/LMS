from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List

if TYPE_CHECKING:

    from src.models.Quiz import Quiz
    from src.models.Quiz_Attempt import Quiz_Attempt
    from src.models.Lecture import Lecture
    from src.models.Question_Option import Question_Option

class Question(SQLModel , table = True):
    question_id :int|None = Field(default=None , primary_key=True)
    question_text :str =Field(nullable=False)
    lecture_id : int =Field(foreign_key='lecture.lecture_id', index=True , nullable=False)
    quiz_id : int =Field(foreign_key='quiz.quiz_id', index=True , nullable=False)

    lecture : "Lecture" = Relationship(back_populates="question")
    quiz : "Quiz" = Relationship(back_populates="question")

    question_option :list["Question_Option"] = Relationship(back_populates="question")
    quiz_attempt :list["Quiz_Attempt"] = Relationship(back_populates="question")

