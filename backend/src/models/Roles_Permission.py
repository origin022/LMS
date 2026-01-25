from sqlmodel import Field, SQLModel ,Relationship
from typing import TYPE_CHECKING  ,List
if TYPE_CHECKING:
    from src.models.Roles import Roles
    from src.models.Permission import Permission

class Roles_Permission(SQLModel ,table = True) :
    role_id: int = Field( foreign_key="roles.roles_id", primary_key=True)
    permission_id: int = Field( foreign_key="permission.permission_id", primary_key=True)

    roles :"Roles" = Relationship(back_populates="roles_permission")
    permission : "Permission" = Relationship(back_populates="roles_permission")


