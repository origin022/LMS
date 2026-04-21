from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.models.Profile import Profile
from src.models.User import User
from src.schemas.profile import UpdateProfile, ProfileUpdateResponse


class ProfileService:

    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int):
        statement = (
            select(Profile)
            .where(Profile.user_id == user_id)
            .options(selectinload(Profile.user))
        )
        result = await db.exec(statement)
        profile = result.first()
        
        if not profile:
            profile = Profile(user_id=user_id)
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            # Re-fetch with options
            statement = (
                select(Profile)
                .where(Profile.user_id == user_id)
                .options(selectinload(Profile.user))
            )
            result = await db.exec(statement)
            profile = result.first()
            
        return profile

    @staticmethod
    async def update_profile_info(
        db: AsyncSession,
        user_id: int,
        data: UpdateProfile
    ):
        # تحديث اسم المستخدم
        if data.name:
            user_stmt = select(User).where(User.user_id == user_id)
            user_res = await db.exec(user_stmt)
            db_user = user_res.first()
            if db_user:
                db_user.name = data.name

        # جلب البروفايل (باستخدام الميثود الجديدة للتأكد من وجوده)
        db_profile = await ProfileService.get_profile(db, user_id)

        if not db_profile:
            return None

        # تحديث البايو
        if data.bio is not None:
            db_profile.bio = data.bio

        await db.commit()

        # إعادة الجلب مع eager loading
        final_stmt = (
            select(Profile)
            .where(Profile.user_id == user_id)
            .options(selectinload(Profile.user))
        )
        final_res = await db.exec(final_stmt)
        return final_res.first()

    @staticmethod
    async def update_profile_picture(
        db: AsyncSession,
        user_id: int,
        image_bytes: bytes
    ):
        db_profile = await ProfileService.get_profile(db, user_id)

        if not db_profile:
            return None

        db_profile.profile_picture_data = image_bytes

        await db.commit()
        await db.refresh(db_profile)

        return db_profile