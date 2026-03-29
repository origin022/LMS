from http.client import HTTPException
from sqlmodel import select, and_ , desc 
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.security import get_owned_obj
from src.schemas.interaction import CommentCreate, CommentUpdate  
from src.models.Comment import Comment
from src.models.Like import Like
from src.models.User import User
from sqlalchemy.orm import selectinload

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
        stmt = select(Comment).where(Comment.comment_id == new_comment.comment_id).options(
            selectinload(Comment.user).selectinload(User.profile)
        )
        res = await db.exec(stmt)
        return res.first()

    @staticmethod
    async def get_lecture_comments(db: AsyncSession, lecture_id: int):
        statement = (
            select(Comment)
            .where(Comment.lecture_id == lecture_id)
            .options(
                selectinload(Comment.user)        
                .selectinload(User.profile)       
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
    


    @staticmethod
    async def update_comment(db: AsyncSession, comment_id: int, current_user: User, data: CommentUpdate):
        db_comment = await get_owned_obj(db, Comment, comment_id, current_user)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_comment, key, value)

        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        return db_comment