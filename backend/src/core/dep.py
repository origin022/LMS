from typing import AsyncGenerator
from fastapi import  HTTPException, status
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
        import traceback
        traceback.print_exc()
        print(f"Database error during session: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is temporarily unavailable."
        )

