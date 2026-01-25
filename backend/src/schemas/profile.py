from pydantic import BaseModel
from typing import Optional

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    name: Optional[str] = None 

class ProfileRead(BaseModel):
    name: str 
    bio: Optional[str] = None
    has_picture: bool = False 

    class Config:
        from_attributes = True