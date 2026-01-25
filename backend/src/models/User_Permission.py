from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models import Permission, User

class User_Permission(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.permission_id", primary_key=True)
    
    is_granted: bool = Field(default=True) 

    user: "User" = Relationship(back_populates="custom_permissions")
    permission: "Permission" = Relationship(back_populates="user_permissions")