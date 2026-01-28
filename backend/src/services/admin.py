from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Permission import Permission
from src.models.Roles_Permission import Roles_Permission
from src.routers import user
from src.models import Roles
from src.schemas.admin import ClassroomCreate, InvitationCreate, RoleCreateWithPermissions
from src.models.Classroom import Classroom
from src.models.Invitation import Invitation
from datetime import datetime, timezone, timedelta
from src.models.User import User
from sqlalchemy.orm import selectinload



class AdminService:

    @staticmethod
    async def create_classroom(db: AsyncSession, data: ClassroomCreate):
        new_class = Classroom(class_name=data.name)
        db.add(new_class)
        await db.commit()
        await db.refresh(new_class)
        return new_class

    @staticmethod
    async def delete_classroom(db: AsyncSession, classroom_id: int):
        statement = select(Classroom).where(Classroom.class_id == classroom_id)
        result = await db.exec(statement)
        classroom = result.first()

        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="هذا الكلاس غير موجود"
            )

        await db.delete(classroom)
        await db.commit()
        return {"message": f"تم حذف الكلاس {classroom.class_name} بنجاح"}

    @staticmethod
    async def create_and_send_invitation(db: AsyncSession, data: InvitationCreate):


        role_stmt = select(Roles).where(Roles.roles_id == data.role_id)
        role_res = await db.exec(role_stmt)
        if not role_res.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رقم الرتبة  غير صالح"
            )


        user_stmt = select(User).where(User.email == data.email)
        user_res = await db.exec(user_stmt)
        if user_res.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="هذا الإيميل مسجل مسبقاً كمستخدم فعلي"
            )

        statement = select(Invitation).where(Invitation.email == data.email)
        result = await db.exec(statement)
        existing_invite = result.first()

        current_now = datetime.now(timezone.utc).replace(tzinfo=None)

        if existing_invite:
            if existing_invite.expires_at > current_now and not existing_invite.is_used:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="هذا الإيميل لديه دعوة صالحة حالياً"
                )
            
            await db.delete(existing_invite)
            await db.commit()

        if not data.role_id:
            raise HTTPException(
            status_code=400,
            detail="يجب اختيار رتبة قبل إرسال الدعوة"
    )
        expiration_date = current_now + timedelta(hours=24)
        new_invitation = Invitation(
            email=data.email,
            role_id=data.role_id,
            expires_at=expiration_date
        )

        db.add(new_invitation)
        await db.commit()
        await db.refresh(new_invitation)
        return new_invitation
    
    @staticmethod
    async def get_all_users(db: AsyncSession, role_id: int = None, state_id: int = None):
        statement = select(User).options(selectinload(User.roles))
    
        if role_id:
            statement = statement.where(User.roles_id == role_id)
        if state_id:
            statement = statement.where(User.state_id == state_id)
        
        result = await db.exec(statement)
        return result.all()
    
    @staticmethod
    async def update_user_permissions(db: AsyncSession, target_user_id: int, new_role_id: int):
        statement = select(User).where(User.user_id == target_user_id)
        user = (await db.exec(statement)).first()
    
        if not user:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")

        if user.roles_id in [1,3,4]:
            raise HTTPException(
                status_code=403, 
                detail="لا يمكنك تعديل صلاحيات الطلبة أو الأساتذة من هنا"
            )
        user.roles_id = new_role_id
        await db.commit()
        return {"message": "تم تحديث الصلاحيات بنجاح"}

    @staticmethod
    async def create_custom_role(db: AsyncSession, data: RoleCreateWithPermissions):
        new_role = Roles(roles_name=data.roles_name)
        db.add(new_role)
        await db.flush()  

        for perm_id in data.permission_ids:
            new_rel = Roles_Permission(
                role_id=new_role.roles_id,
                permission_id=perm_id
            )
            db.add(new_rel)

        await db.commit()
        await db.refresh(new_role)
        return new_role
    
    @staticmethod
    async def get_all_available_permissions(db: AsyncSession):
        statement = select(Permission)
        results = await db.exec(statement)
        return results.all()
    
    @staticmethod
    async def deactivate_manager(db: AsyncSession, manager_id: int):
        statement = select(User).where(User.user_id == manager_id)
        result = await db.exec(statement)
        manager = result.first()
        if not manager:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    
        manager.state_id = 2

        await db.commit()
        return {"message": "تم تعطيل الحساب بنجاح بياناته وكلاساته لا تزال محفوظة."}

    @staticmethod
    async def get_all_classrooms(db: AsyncSession):
        statement = select(Classroom)
        result = await db.exec(statement)
        classrooms = result.all()
        return classrooms

    @staticmethod
    async def get_invitable_roles(db: AsyncSession):
        return (await db.exec(select(Roles).where(Roles.roles_id != 1, Roles.roles_id != 3))).all()