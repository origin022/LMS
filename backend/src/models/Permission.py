from sqlmodel import Field, SQLModel , Relationship
from typing import TYPE_CHECKING  ,List


if TYPE_CHECKING:
    from src.models.Roles_Permission import Roles_Permission
    from src.models import User_Permission



class Permission(SQLModel ,table = True) :
    permission_id :int |None = Field(default=None , primary_key=True)
    name : str = Field(max_length=50 , index= True)

    roles_permission:list["Roles_Permission"] = Relationship(back_populates="permission")
    user_permissions: List["User_Permission"] = Relationship(back_populates="permission") # type: ignore
    
    