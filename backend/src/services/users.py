from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.models.User import User
from sqlmodel.ext.asyncio.session import AsyncSession

class UserService:
    @staticmethod
    async def get_public_user_data(db: AsyncSession, user_id: int):
        statement = (
            select(User)
            .where(User.user_id == user_id)
            .options(selectinload(User.profile))
        )
        result = await db.exec(statement)
        return result.first()