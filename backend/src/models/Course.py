from sqlmodel import Index, SQLModel , Relationship , Field
from typing import TYPE_CHECKING  ,List

if TYPE_CHECKING:

    from src.models.Lecture import Lecture
    from src.models.Question import Question
    from src.models.Enrollment import Enrollment
    from src.models.Classroom import Classroom
    from src.models.Quiz import Quiz

class Course(SQLModel , table = True):
    course_id :int |None = Field(default=None , primary_key= True)
    teacher_id:int = Field(foreign_key= "user.user_id" , nullable=False)
    name :str = Field(max_length=20 , nullable=False)
    class_id :int  = Field(foreign_key='classroom.class_id', index=True , nullable=False)

    lecture : list["Lecture"] = Relationship(back_populates="course")
    enrollment : list["Enrollment"] = Relationship(back_populates="course")
    classroom : "Classroom" = Relationship(back_populates="course")
    quiz: list["Quiz"] = Relationship(back_populates="course",cascade_delete=True)


    

    
 