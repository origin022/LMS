from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:

    from src.models.Teacher_Assignment import Teacher_Assignment
    from src.models.Course import Course
    from src.models.Class_Manager import Class_Manager

class Classroom(SQLModel , table =True) :
    class_id :int |None = Field(default= None , primary_key= True)
    class_name :str = Field(max_length=20  , nullable=False)

    teacher_assignment :list["Teacher_Assignment"] = Relationship(back_populates="classroom", cascade_delete=True)
    course : list["Course"] = Relationship(back_populates="classroom", cascade_delete=True)
    class_image: str | None = Field(default=None)    

    class_manager : list["Class_Manager"] = Relationship(back_populates="classroom", cascade_delete=True)
