from sqlalchemy import Column
from sqlmodel import Field, Index, SQLModel , Relationship
from sqlalchemy import DateTime

from typing import TYPE_CHECKING  ,List, Optional
from datetime import datetime, timezone
from src.models.Roles import Roles
from src.models.State import State




if TYPE_CHECKING:
    from src.models.User_Permission import User_Permission
    from src.models.State import State
    from src.models.Roles import Roles
    from src.models.Teacher_Assignment import Teacher_Assignment
    from src.models.Quiz import Quiz
    from src.models.Quiz_Attempt import Quiz_Attempt
    from src.models.Profile import Profile
    from src.models.Like import Like
    from src.models.Lecture import Lecture
    from src.models.Enrollment import Enrollment
    from src.models.Comment import Comment
    from src.models.Class_Manager import Class_Manager

class User(SQLModel ,table = True) :
  user_id : int | None = Field(default=None , primary_key=True)
  name : str = Field( nullable=False,max_length=100)
  email : str = Field(max_length=100 , unique=True , index=True)
  phone :str = Field(nullable=False)
  hashed_passwored : str = Field( nullable=False , max_length=255)
  created_at: datetime = Field(
    sa_column=Column(
        DateTime(timezone=True),
        nullable=False
    ),
    default_factory=lambda: datetime.now(timezone.utc)
)
  state_id : int   =Field(default=None , foreign_key="state.state_id" , index=True , nullable=False)
  roles_id : int =Field(default=None , foreign_key="roles.roles_id", index=True , nullable=False)


  roles : "Roles"  = Relationship(back_populates="user")
  state : "State"  = Relationship(back_populates="user")
  teacher_assignment : list["Teacher_Assignment"] = Relationship(back_populates="user")
  quiz :list["Quiz"] = Relationship(back_populates="user")
  quiz_attempt :list["Quiz_Attempt"] = Relationship(back_populates="student")
  like : list["Like"] = Relationship(back_populates="user")
  lecture :list["Lecture"] =Relationship(back_populates="user")
  enrollment: list["Enrollment"] = Relationship(back_populates="student")
  comment : list["Comment"] = Relationship(back_populates="user")
  class_manager:list["Class_Manager"] = Relationship(back_populates="manager")
  profile: Optional["Profile"] = Relationship(back_populates="user")
  custom_permissions: List["User_Permission"] = Relationship(back_populates="user")

  __table_args__ = (
        Index("idx_user_state", "roles_id", "state_id"),
    )
  
