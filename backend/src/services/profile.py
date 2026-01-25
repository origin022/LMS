from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Profile import Profile
from src.models.User import User
from src.schemas.profile import ProfileUpdate

class ProfileService:
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int):
        statement = select(Profile).where(Profile.user_id == user_id)
        result = await db.exec(statement)
        return result.first()

    @staticmethod
    async def update_profile_info(db: AsyncSession, user_id: int, data: ProfileUpdate):
        if data.name:
            user_stmt = select(User).where(User.user_id == user_id)
            user_res = await db.exec(user_stmt)
            db_user = user_res.first()
            if db_user:
                db_user.name = data.name

        profile_stmt = select(Profile).where(Profile.user_id == user_id)
        profile_res = await db.exec(profile_stmt)
        db_profile = profile_res.first()
        
        if db_profile:
            if data.bio is not None:
                db_profile.bio = data.bio
            
            await db.commit()
            await db.refresh(db_profile)
        return db_profile

    @staticmethod
    async def update_profile_picture(db: AsyncSession, user_id: int, image_bytes: bytes):
        statement = select(Profile).where(Profile.user_id == user_id)
        result = await db.exec(statement)
        db_profile = result.first()
        
        if db_profile:
            db_profile.profile_picture_data = image_bytes
            await db.commit()
            await db.refresh(db_profile)
        return db_profile