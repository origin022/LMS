from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

from enum import Enum


class UserStatusUpdate(BaseModel):
    user_id: int
    target_state: int 
class UserPermissionRead(BaseModel):
    permission_id: int
    name: str
class PermissionAction(str, Enum):
    block = "block"
    unblock = "unblock"
class LimitPermissionRequest(BaseModel):
    user_id: int
    permission_id: int
    action: PermissionAction

class BatchPermissionUpdate(BaseModel):
    user_id: int
    permissions: List[LimitPermissionRequest]

class ManagerActionResponse(BaseModel):
    status: str = "success"
    message: str
    user_id: int
    new_state: Optional[int] = None

class CustomPermissionResponse(BaseModel):
    user_id: int
    permission_name: str
    message: str

class BasicManagerResponse(BaseModel):
    message: str
    user_id: Optional[int] = None


class PermissionsDashboardResponse(BaseModel):
    user_info: Dict[str, str]
    all_type_permissions: List[Dict[str, Any]]
    restrictions: List[Dict[str, int]]


