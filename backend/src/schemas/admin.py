from pydantic import BaseModel, Field
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from sqlmodel import SQLModel

class ClassroomCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)

class ClassroomRead(BaseModel):
    class_id: int
    class_name: str

    class Config:
        from_attributes = True



class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: Optional[int] = None
    custom_message: Optional[str] = "يسرنا إعلامك بأنه قد تم قبولك للانضمام إلى فريق الإدارة."

class InvitationResponse(BaseModel):
    message: str
    email: str

    


class RoleCreateWithPermissions(SQLModel):
    roles_name: str
    permission_ids: List[int] = Field(default_factory=list)
