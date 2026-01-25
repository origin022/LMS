from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:

    from src.models.Classroom import Classroom
    from src.models.User import User


class Class_Manager(SQLModel , table = True) :
    class_id :int |None = Field (default=None ,primary_key=True ,foreign_key="classroom.class_id")
    manager_id :int |None = Field (default=None ,primary_key=True , foreign_key="user.user_id")

    classroom : "Classroom" = Relationship(back_populates="class_manager")
    manager : "User" = Relationship(back_populates="class_manager")

