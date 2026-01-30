from sqlalchemy import Column
from sqlmodel import DateTime, SQLModel , Field, Relationship
from datetime import datetime, timezone

from typing import TYPE_CHECKING  
if TYPE_CHECKING:

    from src.models.User import User
    from src.models.Course import Course


class Enrollment(SQLModel , table= True):
    enrollment_id :int|None = Field(default=None , primary_key= True)
    student_id : int = Field(foreign_key='user.user_id', index=True , nullable=False)
    course_id : int = Field(foreign_key='course.course_id', index=True , nullable=False)
    created_at: datetime = Field(
    sa_column=Column(DateTime(timezone=True), nullable=False),
    default_factory=lambda: datetime.now(timezone.utc),
    
)

    student : "User" = Relationship(back_populates="enrollment")
    course  :"Course" = Relationship(back_populates="enrollment")

