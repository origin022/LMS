from sqlmodel import SQLModel , Field , Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:
    from src.models.Teacher_Assignment import Teacher_Assignment
    from src.models.Course import Course
    from src.models.Class_Manager import Class_Manager
    from src.models.Department import Department

class Classroom(SQLModel , table =True) :
    class_id :int |None = Field(default= None , primary_key= True)
    class_name :str = Field(max_length=20  , nullable=False)
    department_id: int | None = Field(default=None, foreign_key="department.department_id")
    course : list["Course"] = Relationship(back_populates="classroom", cascade_delete=True)
    class_image: str | None = Field(default=None)    

    class_manager : list["Class_Manager"] = Relationship(back_populates="classroom", cascade_delete=True)
    department: "Department" = Relationship(back_populates="classrooms")
