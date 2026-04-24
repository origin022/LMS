from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.models.Classroom import Classroom
    from src.models.Teacher_Assignment import Teacher_Assignment

class Department(SQLModel, table=True):
    department_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False) # e.g., علمي، أدبي، فني، تقني
    
    classrooms: List["Classroom"] = Relationship(back_populates="department", cascade_delete=True)
    teacher_assignment: List["Teacher_Assignment"] = Relationship(back_populates="department", cascade_delete=True)
