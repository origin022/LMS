from sqlmodel import Index, SQLModel , Relationship , Field
from typing import TYPE_CHECKING  ,List


if TYPE_CHECKING:
    from src.models.User import User
    from src.models.Lecture import Lecture
    from src.models.Question import Question
    from src.models.Enrollment import Enrollment
    from src.models.Classroom import Classroom

class Course(SQLModel , table = True):
    course_id :int |None = Field(default=None , primary_key= True)
    user_id:int = Field(foreign_key= "user.user_id" , nullable=False)
    name :str = Field(max_length=20 , nullable=False)
    class_id :int  = Field(foreign_key='classroom.class_id', index=True , nullable=False)
    course_thumbnail:  str | None = Field(default=None)    


    lecture : list["Lecture"] = Relationship(back_populates="course", cascade_delete=True)
    enrollment : list["Enrollment"] = Relationship(back_populates="course",
            sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "single_parent": True})
    classroom : "Classroom" = Relationship(back_populates="course")
    user: "User" = Relationship(back_populates="courses")


    

    
 