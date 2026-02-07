from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from src.services.EmailSe import EmailService
from src.core.dep import get_session
from src.core.auth import PermissionChecker
from src.schemas.admin import (
    ClassroomCreate, 
    ClassroomRead,
    GetUsersResponse, 
    InvitationCreate, 
    InvitationResponse,
    RoleCreateWithPermissions 
)
from src.services.admin import AdminService

router = APIRouter(prefix="")

check_add_class = PermissionChecker(["create classroom"])
check_delete_class = PermissionChecker(["delete classroom"]) 
INVITE_MANAGER = PermissionChecker(["Add Manager"]) 

VIEW_USERS = PermissionChecker(["view users"])
CHANGE_PERMISSION = PermissionChecker(["Change Permission"])
DELETE_MANAGER = PermissionChecker(["Delete Manager"])


@router.post("/admin/classrooms", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED)
async def create_new_classroom(
    data: ClassroomCreate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(check_add_class)
):
    return await AdminService.create_classroom(db, data)

@router.delete("/admin/classrooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(check_delete_class)
):
    await AdminService.delete_classroom(db, classroom_id)
    return None



@router.post("/admin/managers/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_new_manager(
    data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(INVITE_MANAGER)
):
    new_invitation = await AdminService.create_and_send_invitation(db, data)
    background_tasks.add_task(
        EmailService.send_universal_mail,
        to_email=new_invitation.email,
        token=new_invitation.token,
        subject=" تم توجيه دعوة للانضمام كمدير",
        template="templates.html",
        route="complete-register"
    )
    return {
        "message": "تم إنشاء الدعوة وجاري إرسال الإيميل في الخلفية",
        "email": new_invitation.email,
    }


@router.get("/admin/users" , response_model=list[GetUsersResponse])
async def get_all_users(
    roles_id: Optional[int] = None,
    state_id: Optional[int] = None,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(VIEW_USERS)
):
    return await AdminService.get_all_users(db, roles_id, state_id)

@router.patch("/admin/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: int,
    new_role_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.update_user_permissions(db, user_id, new_role_id)

@router.get("/admin/permissions")
async def get_all_permissions(
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.get_all_available_permissions(db)

@router.post("/admin/roles", status_code=status.HTTP_201_CREATED)
async def create_custom_role(
    data: RoleCreateWithPermissions,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.create_custom_role(db, data)

@router.patch("/admin/managers/{manager_id}/deactivate")
async def deactivate_manager(
    manager_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(DELETE_MANAGER)
):
    return await AdminService.deactivate_manager(db, manager_id)

