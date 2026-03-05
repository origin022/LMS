from sqlmodel import Relationship, SQLModel , Field
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from src.models.User import User


class State(SQLModel , table =True):
    __tablename__ = "state"
    state_id : int | None = Field(default=None , primary_key=True)
    name : str =Field(max_length=10 , nullable=False)

    user : list["User"] = Relationship(back_populates="state")
