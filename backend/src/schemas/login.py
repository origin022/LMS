from pydantic import BaseModel, EmailStr
from typing import Optional



class UserSidebarInfo(BaseModel):
    user_id: int
    email: EmailStr
    role_name: str    

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSidebarInfo