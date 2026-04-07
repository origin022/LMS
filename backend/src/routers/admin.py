from fastapi import APIRouter, BackgroundTasks, Depends, status , File, UploadFile, Request, HTTPException
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
    RoleCreateWithPermissions,
    RoleRead 
)
from src.services.admin import AdminService
from src.core.security import limiter, SENSITIVE_LIMIT, DEFAULT_LIMIT, HEAVY_LIMIT

router = APIRouter(prefix="")

check_add_class = PermissionChecker(["create classroom"])
check_delete_class = PermissionChecker(["delete classroom"]) 
INVITE_MANAGER = PermissionChecker(["Add Manager"]) 

VIEW_USERS = PermissionChecker(["view users"])
CHANGE_PERMISSION = PermissionChecker(["Change Permission"])
DELETE_MANAGER = PermissionChecker(["Delete Manager"])


from fastapi import Form
@router.post("/admin/classrooms", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(SENSITIVE_LIMIT)
async def create_new_classroom(
    request: Request,
    name: str = Form(..., min_length=3, max_length=20),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_session),
    current_user = Depends(check_add_class)
):
    classroom_data = ClassroomCreate(name=name)
    new_class = await AdminService.create_classroom(db, classroom_data)
    
    if image and image.filename:
        # التحقق من نوع الملف (MIME Type)
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="يجب رفع ملف بصيغة صورة فقط (png, jpg, jpeg)"
            )
        await AdminService.upload_classroom_image(db, new_class.class_id, image)
        await db.refresh(new_class)
        
    return new_class
    

@router.delete("/admin/classrooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(SENSITIVE_LIMIT)
async def delete_classroom(
    request: Request,
    classroom_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(check_delete_class)
):
    await AdminService.delete_classroom(db, classroom_id)
    return None



@router.post("/admin/managers/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(SENSITIVE_LIMIT)
async def invite_new_manager(
    request: Request,
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
@limiter.limit(DEFAULT_LIMIT)
async def get_all_users(
    request: Request,
    roles_id: Optional[int] = None,
    state_id: Optional[int] = None,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(VIEW_USERS)
):
    return await AdminService.get_all_users(db, roles_id, state_id)

@router.patch("/admin/users/{user_id}/permissions")
@limiter.limit(SENSITIVE_LIMIT)
async def update_user_permissions(
    request: Request,
    user_id: int,
    new_role_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.update_user_permissions(db, user_id, new_role_id)

@router.get("/admin/permissions")
@limiter.limit(DEFAULT_LIMIT)
async def get_all_permissions(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.get_all_available_permissions(db)

@router.post("/admin/roles", status_code=status.HTTP_201_CREATED)
@limiter.limit(SENSITIVE_LIMIT)
async def create_custom_role(
    request: Request,
    data: RoleCreateWithPermissions,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(CHANGE_PERMISSION)
):
    return await AdminService.create_custom_role(db, data)

@router.patch("/admin/managers/{manager_id}/deactivate")
@limiter.limit(SENSITIVE_LIMIT)
async def deactivate_manager(
    request: Request,
    manager_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(DELETE_MANAGER)
):
    await AdminService.deactivate_manager(db, manager_id)
    return {"message": "تم إلغاء تفعيل المدير"}



@router.get("/admin/roles/invitable", response_model=List[RoleRead])
@limiter.limit(DEFAULT_LIMIT)
async def get_roles_for_invite(
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(INVITE_MANAGER) 
):
    return await AdminService.get_invitable_roles(db)


@router.patch("/admin/classrooms/{classroom_id}/image", status_code=status.HTTP_200_OK)
@limiter.limit(HEAVY_LIMIT)
async def update_classroom_thumbnail(
    request: Request,
    classroom_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    # current_user = Depends(check_add_class) # فَعّلها إذا كنت تستخدم الحماية
):
    # 1. التحقق من نوع الملف (MIME Type)
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="يجب رفع ملف بصيغة صورة فقط (png, jpg, jpeg)"
        )

    # 2. إرسال الملف للسيرفس لمعالجته وحفظه في media/thum
    return await AdminService.upload_classroom_image(db, classroom_id, file)