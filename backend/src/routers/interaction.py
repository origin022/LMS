from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.dep import get_session
from src.core.auth import PermissionChecker, get_current_user
from src.schemas.interaction import CommentCreate, LikeToggle, CommentRead
from src.services import interaction as service
from src.models.User import User
from typing import List

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(PermissionChecker("Comment")) 
):
    return await service.add_comment(db, data, current_user)

@router.get("/comments/{lecture_id}", response_model=List[CommentRead])
async def get_comments(
    lecture_id: int,
    db: AsyncSession = Depends(get_session)

):
    
    comments = await service.get_lecture_comments(db, lecture_id)
    return comments

@router.post("/like")
async def like_lecture(
    data: LikeToggle, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(PermissionChecker("Like"))
):
    return await service.toggle_like(db, data.lecture_id, current_user)