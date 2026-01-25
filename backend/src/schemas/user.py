from typing import Optional
from pydantic import BaseModel, EmailStr, Field



class UserCreate(BaseModel):
      
    name : str = Field(max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    roles_id: int 
    phone:str=  Field(
        ...,
        max_length=20, 
    )
 

  
class UserResponse(BaseModel):
    
    user_id: int
    email: EmailStr
    role_name: Optional[str] = None
    class Config:
        from_attributes = True



class UserRegister(BaseModel):
    name: str
    password: str
    token: str  
    phone:str
