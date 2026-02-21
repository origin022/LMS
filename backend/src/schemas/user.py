from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field



class UserCreate(BaseModel):
      
    name : str = Field(max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    roles_id: int 
    phone:str=  Field(
        ...,
        max_length=20, 
    )
 

  
class UserRead(BaseModel):
    
    user_id: int
    name: str
    email: EmailStr
    role_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)




class UserInvitationRegister(BaseModel):
    name: str
    password: str
    token: str  
    phone:str


