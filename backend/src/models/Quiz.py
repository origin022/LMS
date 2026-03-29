from sqlmodel import SQLModel , Field , Relationship, true
from typing import TYPE_CHECKING  ,List


if TYPE_CHECKING:
    from src.models.Lecture import Lecture
    from src.models.User import User
    from src.models.Question import Question
    from src.models.Quiz_Attempt import Quiz_Attempt


class Quiz(SQLModel, table = True):
    quiz_id : int |None = Field(default=None , primary_key= True)
    title :str =Field(nullable=False)
    lecture_id : int = Field(foreign_key='lecture.lecture_id', index=True , nullable=True) 
    user_id : int = Field(foreign_key='user.user_id', index=True , nullable=False)

    user  :"User" = Relationship(back_populates="quiz")

    question: list["Question"] = Relationship(back_populates="quiz",
            sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "single_parent": True})
    lecture : "Lecture" = Relationship(back_populates="quiz")
    quiz_attempt : list["Quiz_Attempt"] = Relationship(back_populates="quiz",
            sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "single_parent": True})
    
    