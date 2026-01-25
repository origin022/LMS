from sqlmodel import Column, LargeBinary, SQLModel , Field ,  Relationship
from typing import TYPE_CHECKING  , Optional
if TYPE_CHECKING:

    from src.models.User import User
    from src.models.State import State

class Profile(SQLModel , table =True) :
    user_id : int| None = Field(default= None , primary_key=True , foreign_key="user.user_id")
    profile_picture_data: Optional[bytes] = Field(
        sa_column=Column(LargeBinary, nullable=True)
    )
    bio :str =Field(max_length=50 ,nullable=True) 
    user: "User" = Relationship(back_populates="profile", sa_relationship_kwargs={"uselist": False})


