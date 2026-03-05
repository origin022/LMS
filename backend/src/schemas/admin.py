from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, EmailStr
from typing import List, Optional


class ClassroomCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)

class ClassroomRead(BaseModel):
    class_id: int
    class_name: str

    model_config = ConfigDict(from_attributes=True)




class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: int
    custom_message: Optional[str] = "يسرنا إعلامك بأنه قد تم قبولك للانضمام إلى فريق الإدارة."

class InvitationResponse(BaseModel):
    message: str
    email: str

    
class GetUsersResponse(BaseModel):
    name :str
    created_at:datetime
    email:str
    phone:str
    roles_name:str
    state_name:str


class RoleCreateWithPermissions(BaseModel):
    roles_name: str
    permission_id: List[int] = Field(default_factory=list)






class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None 

class RoleUpdate(BaseModel):
    roles_name: Optional[str] = None
    permission_id: Optional[List[int]] = None


class RoleRead(BaseModel):
    roles_id: int
    roles_name: str