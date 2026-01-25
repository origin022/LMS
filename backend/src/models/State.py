from sqlmodel import Relationship, SQLModel , Field
from typing import TYPE_CHECKING , List

if TYPE_CHECKING:
    from src.models.User import User
    from src.models.Profile import Profile


class State(SQLModel , table =True):
    state_id : int | None = Field(default=None , primary_key=True)
    name : str =Field(max_length=10 , nullable=False)

    user : list["User"] = Relationship(back_populates="state")
