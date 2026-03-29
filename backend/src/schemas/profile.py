from pydantic import BaseModel, ConfigDict
from typing import Optional

class UpdateProfile(BaseModel):
    bio: Optional[str] = None
    name: Optional[str] = None 

class ProfileUpdateResponse(BaseModel):
    name: str
    bio: str
    has_picture: bool

class ReadProfile(BaseModel):
    name: str 
    bio: Optional[str] = None
    picture: bool = False 

    model_config = ConfigDict(from_attributes=True)
