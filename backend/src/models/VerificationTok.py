from enum import Enum
from datetime import datetime
from typing import Optional
from sqlmodel import DateTime, SQLModel, Field, Relationship

class TokenType(str, Enum):
    MAGIC_LINK = "magic_link"
    PASSWORD_RESET = "password_reset"

class VerificationToken(SQLModel, table=True):
    __tablename__ = "verification_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True)
    email: str = Field(index=True) 
    type: TokenType = Field(default=TokenType.MAGIC_LINK)
    expires_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False
    )
   