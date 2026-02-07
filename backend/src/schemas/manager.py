from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Optional, Any

from enum import Enum


class UpdateUserStatus(BaseModel):
    user_id: int
    target_state: int 
class ReadUserPermission(BaseModel):
    permission_id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class PermissionAction(str, Enum):
    block = "block"
    unblock = "unblock"
class CreatLimitPermission(BaseModel):
    user_id: int
    permission_id: int
    action: PermissionAction

class UpdateBatchPermission(BaseModel):
    user_id: int
    permissions: List[CreatLimitPermission]

class ReadManagerAction(BaseModel):
    status: str = "success"
    message: str
    model_config = ConfigDict(from_attributes=True)



class CustomPermissionResponse(BaseModel):
    message: str
    model_config = ConfigDict(from_attributes=True)



class BasicManagerResponse(BaseModel):
    message: str
    model_config = ConfigDict(from_attributes=True)



class UserPermissionInfo(BaseModel):
    permission_id: int
    name: str
    status: str  

class PermissionsDashboardResponse(BaseModel):
    name: str
    role_name: str
    permissions: List[UserPermissionInfo] 
    
    class Config:
        from_attributes = True