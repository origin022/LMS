from sqlmodel import DateTime, SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, LargeBinary  
from datetime import datetime, timezone

if TYPE_CHECKING:
    from src.models.Lecture import Lecture

class Media(SQLModel, table=True):
    media_id: Optional[int] = Field(default=None, primary_key=True)
    lecture_id: int = Field(foreign_key="lecture.lecture_id", index=True)
    
    file_path: str = Field(nullable=False)  
    file_name: str = Field(nullable=False)
    mime_type: str = Field(nullable=False)  
    created_at:  datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True), 
)
    

    lecture: "Lecture" = Relationship(back_populates="media")