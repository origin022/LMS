from datetime import datetime, timezone
from sqlmodel import Index, SQLModel , Field, Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:

    from src.models.Question import Question
    from src.models.Media import Media
    from src.models.Like import Like
    from src.models.Course import Course
    from src.models.User import User
    from src.models.Comment import Comment

class Lecture(SQLModel , table = True) :
    lecture_id :int |None = Field(default=None , primary_key= True)
    title :str = Field(max_length=30 , nullable=False)
    description :str = Field(nullable=True)
    course_id : int  = Field(foreign_key='course.course_id', index=True , nullable=False)
    user_id : int = Field(foreign_key='user.user_id', index=True , nullable=False)
    created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    question : list["Question"]= Relationship(back_populates="lecture")
    media : list["Media"]=Relationship(back_populates="lecture")
    like : list["Like"] = Relationship(back_populates="lecture")
    comment : list["Comment"]  =Relationship(back_populates="lecture")


    course : "Course" = Relationship(back_populates="lecture")
    user : "User" = Relationship(back_populates="lecture")

    




    __table_args__ = (

        Index("idx_lecture_course_user", "course_id", "user_id"),
        )