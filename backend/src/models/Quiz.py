from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:
    from src.models.Course import Course
    from src.models.User import User
    from src.models.Question import Question

class Quiz(SQLModel, table = True):
    quiz_id : int |None = Field(default=None , primary_key= True)
    title :str =Field(nullable=False)
    description :str = Field(nullable=True)
    duration_minute: int | None = Field(nullable=False)
    course_id : int = Field(foreign_key='course.course_id', index=True , nullable=False) 
    user_id : int = Field(foreign_key='user.user_id', index=True , nullable=False)

    course : "Course"  =Relationship(back_populates="quiz")
    user  :"User" = Relationship(back_populates="quiz")

    question: list["Question"] = Relationship(back_populates="quiz")
    
    