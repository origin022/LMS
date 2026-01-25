from sqlmodel import Field, Index, Relationship, SQLModel
from typing import TYPE_CHECKING , List
if TYPE_CHECKING:
    from src.models.Roles_Permission import Roles_Permission
    from src.models.User import User 
class Roles(SQLModel , table = True):
    roles_id : int = Field(default=None,primary_key=True)
    roles_name : str = Field(nullable=False,max_length=50)

    user : list["User"] = Relationship(back_populates="roles")
    roles_permission : list["Roles_Permission"] = Relationship(back_populates="roles")


