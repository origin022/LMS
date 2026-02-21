from sqlmodel import DateTime, Index, SQLModel , Field  , Relationship
from datetime import datetime, timezone

from typing import TYPE_CHECKING  
if TYPE_CHECKING:

    from src.models.User import User
    from src.models.Lecture import Lecture


class Comment(SQLModel , table = True):
    comment_id :int |None = Field(default=None , primary_key=True)
    user_id :int = Field(foreign_key='user.user_id', index=True , nullable=False)
    lecture_id : int = Field(foreign_key='lecture.lecture_id', index=True , nullable=False)
    text :str = Field(nullable=False)
    submission_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True) ,
        nullable=False
    )
    
    user : "User" = Relationship(back_populates="comment")
    lecture : "Lecture" = Relationship(back_populates="comment")


    __table_args__ = (
        Index("idx_comment_lecture_time", "lecture_id", "submission_time"),
        Index("idx_comment_user_lecture", "user_id", "lecture_id"),
    )
