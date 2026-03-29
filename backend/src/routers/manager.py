from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.core.auth import PermissionChecker
from src.core.dep import get_session

from src.services.manager import Manager
from src.schemas.manager import BasicManagerResponse, CustomPermissionResponse, PermissionsDashboardResponse, ReadManagerAction, UpdateUserStatus, CreatLimitPermission

router = APIRouter(
    prefix="",
    tags=["Manager Operations"]
)



@router.post("/update-status", response_model=ReadManagerAction)
async def update_user_status(
    data: UpdateUserStatus, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker("Add Teacher"))
    ):
    return await Manager.update_user_status(db, data)

@router.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK, response_model=BasicManagerResponse)
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Delete user"]))

):
    return await Manager.delete_user(db, user_id)

@router.get("/permissions-dashboard/{user_id}", response_model=PermissionsDashboardResponse)
async def get_permissions_dashboard(
    user_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view users"]))
):
    return await Manager.get_user_permissions(db, user_id)

@router.post("/toggle-permission", response_model=CustomPermissionResponse)
async def toggle_permission(
    data: CreatLimitPermission, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Limiting permission"]))

):
    return await Manager.toggle_user_permission(db, data)

@router.delete("/delete-comment/{comment_id}", status_code=status.HTTP_200_OK, response_model=BasicManagerResponse)
async def delete_comment(
    comment_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Delete Comment"]))
):
    return await Manager.delete_comment(db, comment_id)