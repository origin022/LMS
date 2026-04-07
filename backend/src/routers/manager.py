from fastapi import APIRouter, Depends, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.core.auth import PermissionChecker, get_current_user
from src.core.dep import get_session
from src.models.User import User

from src.services.manager import Manager
from src.schemas.manager import BasicManagerResponse, CustomPermissionResponse, PermissionsDashboardResponse, ReadManagerAction, UpdateUserStatus, CreatLimitPermission, CommentRead
from src.core.security import limiter, SENSITIVE_LIMIT, DEFAULT_LIMIT

router = APIRouter(
    prefix="",
    tags=["Manager Operations"]
)


@router.get("/my-dashboard", response_model=PermissionsDashboardResponse)
@limiter.limit(DEFAULT_LIMIT)
async def get_my_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await Manager.get_my_permissions(db, current_user)


@router.post("/update-status", response_model=ReadManagerAction)
@limiter.limit(SENSITIVE_LIMIT)
async def update_user_status(
    request: Request,
    data: UpdateUserStatus, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker("Add Teacher"))
    ):
    return await Manager.update_user_status(db, data)

@router.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK, response_model=BasicManagerResponse)
@limiter.limit(SENSITIVE_LIMIT)
async def delete_user(
    request: Request,
    user_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Delete user"]))

):
    return await Manager.delete_user(db, user_id)

@router.get("/permissions-dashboard/{user_id}", response_model=PermissionsDashboardResponse)
@limiter.limit(DEFAULT_LIMIT)
async def get_permissions_dashboard(
    request: Request,
    user_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view users"]))
):
    return await Manager.get_user_permissions(db, user_id)

@router.get("/permissions-dashboard/by-email/{email}", response_model=PermissionsDashboardResponse)
@limiter.limit(DEFAULT_LIMIT)
async def get_permissions_dashboard_by_email(
    request: Request,
    email: str, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["view users"]))
):
    return await Manager.get_user_permissions_by_email(db, email)

@router.post("/toggle-permission", response_model=CustomPermissionResponse)
@limiter.limit(SENSITIVE_LIMIT)
async def toggle_permission(
    request: Request,
    data: CreatLimitPermission, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Limiting permission"]))

):
    return await Manager.toggle_user_permission(db, data)

@router.delete("/delete-comment/{comment_id}", status_code=status.HTTP_200_OK, response_model=BasicManagerResponse)
@limiter.limit(SENSITIVE_LIMIT)
async def delete_comment(
    request: Request,
    comment_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Delete Comment"]))
):
    return await Manager.delete_comment(db, comment_id)

@router.get("/recent-comments", response_model=List[CommentRead])
@limiter.limit(DEFAULT_LIMIT)
async def get_recent_comments(
    request: Request,
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(PermissionChecker(["Delete Comment"]))
):
    return await Manager.get_recent_comments(db, limit)