from sqlmodel import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Roles import Roles
from src.models.Roles_Permission import Roles_Permission
from src.models.User import User
from src.models.User_Permission import User_Permission
from src.schemas.manager import PermissionAction, UpdateUserStatus, CreatLimitPermission
from src.models.Comment import Comment

class Manager:




    @staticmethod
    async def _get_target_user(db: AsyncSession, user_id: int) -> User:
        statement = select(User).where(User.user_id == user_id)
        result = await db.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(status_code=404, detail="هذا المستخدم غير موجود في النظام")
        
        if user.roles_id in [1, 2]:
            raise HTTPException(
                status_code=403, 
                detail="لا يمكن إجراء هذه العملية على حسابات الإدارة (آدمن/مدير)"
            )
        
        return user
    

    @staticmethod
    async def update_user_status(db: AsyncSession, data: UpdateUserStatus):
        user = await Manager._get_target_user(db, data.user_id)

        status_map = {1: "نشط", 2: "معلق", 3: "محظور"}
        if data.target_state not in status_map:
            raise HTTPException(
                status_code=400,
                detail="قيمة الحالة غير صحيحة"
            )
        user.state_id = data.target_state
        await db.commit()
        await db.refresh(user)

        return {
            "message": f"تم تغيير حالة المستخدم إلى {status_map[data.target_state]}",
            "new_state": user.state_id
        }

    
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        user = await Manager._get_target_user(db, user_id)
        
        await db.delete(user)
        await db.commit()
        
        return {"message": "تم حذف المستخدم نهائياً", "user_id": user_id}

   
    @staticmethod
    async def toggle_user_permission(db: AsyncSession, data: CreatLimitPermission):
        await Manager._get_target_user(db, data.user_id)

        stmt = select(User_Permission).where(
            User_Permission.user_id == data.user_id,
            User_Permission.permission_id == data.permission_id
        )
        existing = (await db.exec(stmt)).first()

        if data.action == PermissionAction.block:
            if existing:
                raise HTTPException(status_code=400, detail="المستخدم ممنوع مسبقاً")
            
            new_entry = User_Permission(user_id=data.user_id, permission_id=data.permission_id)
            db.add(new_entry)
            await db.commit()
            return {"status": "success", "message": "تم المنع بنجاح"}

        elif data.action == PermissionAction.unblock:
            if not existing:
                raise HTTPException(status_code=400, detail="المستخدم غير ممنوع أصلاً")
            
            await db.delete(existing)
            await db.commit()
            return {"status": "success", "message": "تم إلغاء المنع بنجاح"}
    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: int):
        statement = (
            select(User)
            .where(User.user_id == user_id)
            .options(
                selectinload(User.roles)
                    .selectinload(Roles.roles_permission)
                    .selectinload(Roles_Permission.permission),
                selectinload(User.custom_permissions)
                    .selectinload(User_Permission.permission)
        )
    )
        result = await db.exec(statement)
        target_user = result.first()

        if not target_user:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")

        restricted_ids = {cp.permission_id for cp in target_user.custom_permissions}

        final_permissions = []

        for rp in target_user.roles.roles_permission:
            p = rp.permission
            if p.permission_id in restricted_ids:
                status = "محظور"
            else:
                status = "مسموح للنوع"
            
            final_permissions.append({
                "permission_id": p.permission_id,
                "name": p.name,
                "status": status
        }   
        )

        role_perm_ids = {rp.permission_id for rp in target_user.roles.roles_permission}
        for cp in target_user.custom_permissions:
            if cp.permission_id not in role_perm_ids:
                final_permissions.append({
                    "permission_id": cp.permission.permission_id,
                    "name": cp.permission.name,
                    "status": "محظور (إضافي)"
            }   
            )

        return {
            "name": target_user.name,
            "role_name": "أستاذ" if target_user.roles_id == 3 else "طالب",
            "permissions": final_permissions
    }


    @staticmethod
    async def delete_comment(db: AsyncSession, comment_id: int):
        stmt = select(Comment).where(Comment.comment_id == comment_id)
        result = await db.exec(stmt)
        comment = result.first()

        if not comment:
            raise HTTPException(status_code=404, detail="التعليق غير موجود أو تم حذفه مسبقاً")

        await db.delete(comment)
        await db.commit()
        return {"message": "تم حذف التعليق بنجاح بواسطة الإدارة", "comment_id": comment_id}