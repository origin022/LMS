from sqlmodel import select, and_ , desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.interaction import CommentCreate  
from src.models.Comment import Comment
from src.models.Like import Like
from src.models.User import User
from sqlalchemy.orm import joinedload

class InteractionS:
    @staticmethod
    async def add_comment(db: AsyncSession, comment_data: CommentCreate, current_user: User):
        new_comment = Comment(
            text=comment_data.text,
            lecture_id=comment_data.lecture_id,
            user_id=current_user.user_id
        )
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return new_comment

    @staticmethod
    async def get_lecture_comments(db: AsyncSession, lecture_id: int):
        statement = (
            select(Comment)
            .where(Comment.lecture_id == lecture_id)
            .options(
                joinedload(Comment.user)        
                .joinedload(User.profile)       
            )
            .order_by(desc(Comment.submission_time)) 
        )
        result = await db.exec(statement)
        return result.all()

    @staticmethod
    async def toggle_like(db: AsyncSession, lecture_id: int, current_user: User):
        statement = select(Like).where(
            and_(Like.lecture_id == lecture_id, Like.user_id == current_user.user_id)
        )
        result = await db.exec(statement)
        existing_like = result.first()

        if existing_like:
            await db.delete(existing_like)
            await db.commit()
            return {"action": "unliked"}
        
        new_like = Like(lecture_id=lecture_id, user_id=current_user.user_id)
        db.add(new_like)
        await db.commit()
        return {"action": "liked"}