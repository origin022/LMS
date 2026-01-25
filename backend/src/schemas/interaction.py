from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentUserDetail(BaseModel):
    name: str
    profile_picture_url: Optional[str] = None

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    lecture_id: int

class CommentResponse(BaseModel):
    comment_id: int
    text: str
    submission_time: datetime 

    class Config:
        from_attributes = True

class CommentRead(BaseModel):
    comment_id: int
    text: str
    submission_time: datetime  
    user: CommentUserDetail    
    
    class Config:
        from_attributes = True

class LikeToggle(BaseModel):
    lecture_id: Optional[int] = None
    comment_id: Optional[int] = None