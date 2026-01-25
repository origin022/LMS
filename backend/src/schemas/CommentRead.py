from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentUserDetail(BaseModel):
    name: str
    profile_picture_url: Optional[str] = None

class CommentRead(BaseModel):
    comment_id: int
    text: str
    submission_time: datetime  
    user: CommentUserDetail    
    class Config:
        from_attributes = True