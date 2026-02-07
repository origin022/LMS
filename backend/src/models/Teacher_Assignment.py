from sqlmodel import SQLModel , Field ,Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:
    from src.models.User import User
    from src.models.Classroom import Classroom


class Teacher_Assignment(SQLModel , table = True):
    user_id :int|None = Field (primary_key= True ,foreign_key="user.user_id")
    class_id :int|None = Field( foreign_key='classroom.class_id', index=True)

    classroom : "Classroom" = Relationship(back_populates="teacher_assignment")
    user :"User"  = Relationship(back_populates="teacher_assignment")