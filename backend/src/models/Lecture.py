from datetime import datetime, timezone
from sqlmodel import Column, DateTime, Index, SQLModel , Field, Relationship
from typing import TYPE_CHECKING  ,List, Optional

if TYPE_CHECKING:

    from src.models.Question import Question
    from src.models.Media import Media
    from src.models.Like import Like
    from src.models.Course import Course
    from src.models.User import User
    from src.models.Comment import Comment
    from src.models.Quiz import Quiz


class Lecture(SQLModel , table = True) :
    lecture_id :int |None = Field(default=None , primary_key= True)
    title :str = Field(max_length=100 , nullable=False)
    description :str = Field(nullable=True)
    course_id : int  = Field(foreign_key='course.course_id', index=True , nullable=False)
    user_id : int = Field(foreign_key='user.user_id', index=True , nullable=False)
    created_at: datetime = Field(
    sa_column=Column(
    DateTime(timezone=True),
    nullable=False
    ),
    default_factory=lambda: datetime.now(timezone.utc)
)
    text : Optional[str] = Field(default=None, nullable=True)

    media : list["Media"]=Relationship(back_populates="lecture",cascade_delete=True)
    like : list["Like"] = Relationship(back_populates="lecture",cascade_delete=True)
    comment : list["Comment"]  =Relationship(back_populates="lecture",cascade_delete=True)
    lecture_image:  str | None = Field(default=None)    


    course : "Course" = Relationship(back_populates="lecture")
    user : "User" = Relationship(back_populates="lecture" )
    quiz : list["Quiz"] = Relationship(back_populates="lecture", cascade_delete=True)

    




    __table_args__ = (

        Index("idx_lecture_course_user", "course_id", "user_id"),
        )