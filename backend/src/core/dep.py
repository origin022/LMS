from typing import AsyncGenerator, List 
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession    
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import config 
   

engine = create_async_engine(
    str(config.SQLALCHEMY_DATABASE_URI), 
    echo=False 
) 
    
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with AsyncSession(engine) as session:
            yield session
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error during session: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is temporarily unavailable."
        )

