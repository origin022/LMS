from datetime import datetime
from typing import Optional
from sqlmodel import Column, DateTime, SQLModel , Field, UniqueConstraint 

class Student_Mastery(SQLModel, table=True):
    mastery_id: Optional[int] = Field(default=None , primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", index=True)
    course_id: int = Field(foreign_key="course.course_id", index=True) 
    mastery_score: float = Field(default=0.0) 
    last_updated: datetime = Field(
    sa_column=Column( DateTime(timezone=True),nullable=False))
    current_difficulty: int = Field(default=1)
    correct_streak: int = Field(default=0)


    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="unique_user_course_mastery"),
    )