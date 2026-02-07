from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReadeUserPublic(BaseModel):
    user_id: int
    name: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
