from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.State import State
from src.models.Permission import Permission
from src.models.Roles_Permission import Roles_Permission
from src.models.Roles import Roles 
from src.schemas.admin import ClassroomCreate, GetUsersResponse, InvitationCreate, RoleCreateWithPermissions 
from src.models.Classroom import Classroom
from src.models.Invitation import Invitation
from datetime import datetime, timezone, timedelta
from src.models.User import User
from src.models.Course import Course
from src.models.Teacher_Assignment import Teacher_Assignment
from src.models.Department import Department
from sqlalchemy.orm import selectinload, joinedload
from fastapi import UploadFile
import os
import uuid



class AdminService:
    UPLOAD_DIR = os.path.join("media", "thum")
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    @staticmethod
    async def create_classroom(db: AsyncSession, data: ClassroomCreate):
        new_class = Classroom(
            class_name=data.name,
            department_id=data.department_id
        )
        db.add(new_class)
        await db.commit()
        await db.refresh(new_class)
        return new_class

    @staticmethod
    async def create_department(db: AsyncSession, name: str):
        department = Department(name=name)
        db.add(department)
        await db.commit()
        await db.refresh(department)
        return department

    @staticmethod
    async def get_departments(db: AsyncSession):
        statement = select(Department)
        result = await db.exec(statement)
        return result.all()

    @staticmethod
    async def delete_department(db: AsyncSession, department_id: int):
        statement = select(Department).where(Department.department_id == department_id)
        result = await db.exec(statement)
        department = result.first()
        if not department:
            raise HTTPException(status_code=404, detail="القسم غير موجود")
        await db.delete(department)
        await db.commit()
        return {"message": "تم حذف القسم بنجاح"}
    

    @staticmethod
    async def upload_classroom_image(db: AsyncSession, classroom_id: int, file: UploadFile):
        statement = select(Classroom).where(Classroom.class_id == classroom_id)
        result = await db.exec(statement)
        classroom = result.first()

        if not classroom:
            raise HTTPException(status_code=404, detail="الكلاس غير موجود")

        try:
            content = await file.read()

            # التحقق من حجم الملف
            if len(content) > AdminService.MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="حجم الصورة يتجاوز الحد المسموح (5MB)")

            extension = file.filename.split(".")[-1].lower()
            file_name = f"cls_{classroom_id}_{uuid.uuid4().hex}.{extension}"
            
            os.makedirs(AdminService.UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(AdminService.UPLOAD_DIR, file_name)

            with open(file_path, "wb") as f:
                f.write(content)

            if classroom.class_image and os.path.exists(classroom.class_image):
                try: os.remove(classroom.class_image)
                except: pass

            classroom.class_image = file_path.replace("\\", "/")
        
            await db.commit()
            await db.refresh(classroom)

            return {"message": "تم الرفع بنجاح", "image_url": file_path}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_classroom(db: AsyncSession, classroom_id: int):
        statement = select(Classroom).where(Classroom.class_id == classroom_id).options(selectinload(Classroom.course).selectinload(Course.lecture))
        result = await db.exec(statement)
        classroom = result.first()

        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="هذا الكلاس غير موجود"
            )

        for course in classroom.course:
            for lec in course.lecture:
                if lec.lecture_image and os.path.exists(lec.lecture_image):
                    try: os.remove(lec.lecture_image)
                    except: pass
            if course.course_thumbnail and os.path.exists(course.course_thumbnail):
                try: os.remove(course.course_thumbnail)
                except: pass
                
        if classroom.class_image and os.path.exists(classroom.class_image):
            try: os.remove(classroom.class_image)
            except: pass

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
    async def get_all_users(db: AsyncSession, roles_id: int = None, state_id: int = None):
        stmt = (
            select(User)
            .options(
                selectinload(User.roles),
                selectinload(User.state),
                selectinload(User.teacher_assignment).selectinload(Teacher_Assignment.classroom)
            )
        )
    
        if roles_id is not None:
            stmt = stmt.where(User.roles_id == roles_id)
        if state_id is not None:
            stmt = stmt.where(User.state_id == state_id)
        
        result = await db.exec(stmt)   
        users = result.all()

        return [
            GetUsersResponse(
                user_id=u.user_id,
                name=u.name,
                email=u.email,
                phone=u.phone,
                roles_id=u.roles_id,
                roles_name=u.roles.roles_name if u.roles else "مستخدم",
                state_id=u.state_id,
                state_name=u.state.name if u.state else "غير معروف",
                created_at=u.created_at,
                class_name=", ".join([ta.classroom.class_name for ta in u.teacher_assignment if ta.classroom]) if u.teacher_assignment else None
            ) for u in users
        ]
    
   
    @staticmethod
    async def create_custom_role(db: AsyncSession, data: RoleCreateWithPermissions):
        new_role = Roles(roles_name=data.roles_name)
        db.add(new_role)
        await db.flush()  

        for perm_id in data.permission_id:
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
        statement = select(Permission).join(Roles_Permission, Roles_Permission.permission_id == Permission.permission_id).where(Roles_Permission.role_id != 1, Roles_Permission.role_id != 3, Roles_Permission.role_id != 4)
        results = await db.exec(statement)
        return results.all()
    
    @staticmethod
    async def deactivate_manager(db: AsyncSession, manager_id: int):
        statement = select(User).where(User.user_id == manager_id)
        result = await db.exec(statement)
        manager = result.first()
        if not manager:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")
        if manager.state_id==1 :
            manager.state_id = 2
            await db.commit()
            return {"message": "تم تعطيل الحساب بنجاح بياناته وكلاساته لا تزال محفوظة."}
        if manager.state_id==2 :
            manager.state_id = 1
            await db.commit()
            return {"message": "تم تفعيل الحساب بنجاح بياناته وكلاساته لا تزال محفوظة."}
        
        else :
              raise HTTPException(
            status_code=400,
            detail="حالة المستخدم غير معروفة"
        )


       
    @staticmethod
    async def get_all_classrooms(db: AsyncSession):
        statement = select(Classroom).options(
            selectinload(Classroom.course),
            selectinload(Classroom.department)
        )
        result = await db.exec(statement)
        return result.unique().all()

    @staticmethod
    async def get_invitable_roles(db: AsyncSession):
        return (await db.exec(select(Roles).where(
            Roles.roles_id != 1, 
            Roles.roles_id != 3, 
            Roles.roles_id != 4
        ))).all()
    


