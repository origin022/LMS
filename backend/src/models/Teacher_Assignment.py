from sqlmodel import SQLModel , Field ,Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:
    from src.models.User import User
    from src.models.Department import Department


class Teacher_Assignment(SQLModel , table = True):
    user_id :int|None = Field (primary_key= True ,foreign_key="user.user_id")
    department_id :int|None = Field( foreign_key='department.department_id', index=True)

    department : "Department" = Relationship(back_populates="teacher_assignment")
    user :"User"  = Relationship(back_populates="teacher_assignment")