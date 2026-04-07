from fastapi import APIRouter, Depends, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.dep import get_session
from src.core.auth import PermissionChecker, get_current_user
from src.schemas.interaction import CommentCreate, CommentUpdate, Commentred, LikeToggle, CommentResponse
from src.services.interaction import InteractionS as service
from src.core.security import limiter, SENSITIVE_LIMIT, DEFAULT_LIMIT
from fastapi import WebSocket, WebSocketDisconnect
from src.core.wepsocket import manager
from src.models.User import User
from typing import List
import asyncio

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/lectures/{lecture_id}/comments", status_code=status.HTTP_201_CREATED, response_model=Commentred)
@limiter.limit(SENSITIVE_LIMIT)
async def create_comment(
    lecture_id: int, 
    data: CommentCreate, 
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(PermissionChecker(["Comment"])) 
):
    c = await service.add_comment(db, data, current_user)
    
    pic_url = None
    if c.user and c.user.profile and c.user.profile.profile_picture_data:
        pic_url = f"{request.base_url}api/v1/users/{c.user_id}/picture"
    
    comment_payload = {
        "comment_id": c.comment_id,
        "text": c.text,
        "submission_time": c.submission_time.isoformat() if hasattr(c.submission_time, 'isoformat') else str(c.submission_time),
        "user_id": c.user_id,
        "user": {
            "name": c.user.name,
            "profile_picture_url": pic_url
        }
    }

    asyncio.create_task(
        manager.broadcast_to_lecture(lecture_id, comment_payload)
    )       
    return comment_payload
@router.get("/lectures/{lecture_id}/comments", response_model=List[Commentred])
@limiter.limit(DEFAULT_LIMIT)
async def get_comments(
    lecture_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    comments = await service.get_lecture_comments(db, lecture_id)
    result = []
    for c in comments:
        pic_url = None
        if c.user and c.user.profile and c.user.profile.profile_picture_data:
            # The URL needs to match the frontend expectations, or we can just pass a truthy string
            pic_url = f"{request.base_url}api/v1/users/{c.user_id}/picture"
        
        result.append({
            "comment_id": c.comment_id,
            "text": c.text,
            "submission_time": c.submission_time,
            "user_id": c.user_id,
            "user": {
                "name": c.user.name,
                "profile_picture_url": pic_url
            }
        })
    return result

@router.post("/lectures/{lecture_id}/like" , response_model=LikeToggle)
@limiter.limit(SENSITIVE_LIMIT)
async def like_lecture(
    request: Request,
    lecture_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(PermissionChecker(["Like"]))
):
    return await service.toggle_like(db, lecture_id, current_user)




@router.patch("/comment/{comment_id}", response_model=CommentUpdate)
@limiter.limit(SENSITIVE_LIMIT)
async def update_comment(
    request: Request,
    comment_id: int,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    return await service.update_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user,
        data=data
    )




import asyncio

@router.websocket("/ws/{lecture_id}")
async def lecture_comments_websocket(websocket: WebSocket, lecture_id: int):
    await manager.connect(websocket, lecture_id)
    try:
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.disconnect(websocket, lecture_id)