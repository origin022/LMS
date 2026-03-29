from pydantic import BaseModel, ConfigDict, Field
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
    model_config = ConfigDict(from_attributes=True)




class Commentred(BaseModel):
    comment_id: int
    text: str
    submission_time: datetime  
    user_id: int
    user: CommentUserDetail   
    model_config = ConfigDict(from_attributes=True)

     
     
    

 

class CommentUpdate(BaseModel):
    text: str

class LikeToggle(BaseModel):
    lecture_id: Optional[int] = None




class CommentUserDetail(BaseModel):
    name: str
    profile_picture_url: Optional[str] = None

class CommentRead(BaseModel):
    comment_id: int
    text: str
    submission_time: datetime  
    user: CommentUserDetail   
     
    model_config = ConfigDict(from_attributes=True)
