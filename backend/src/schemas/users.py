from pydantic import BaseModel
from typing import Optional

class UserPublic(BaseModel):
    user_id: int
    name: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True