from sqlmodel import SQLModel , Field,Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:

    from src.models.Lecture import Lecture
    from src.models.User import User

class Like(SQLModel , table = True):
    like_id : int |None =Field(default=None , primary_key=True)
    user_id : int  =Field(default=None , foreign_key="user.user_id", index=True , nullable=False)
    lecture_id : int =Field(default=None , foreign_key="lecture.lecture_id", index=True ,nullable=False)

    user : "User" = Relationship(back_populates="like")
    lecture : "Lecture" = Relationship(back_populates="like")



