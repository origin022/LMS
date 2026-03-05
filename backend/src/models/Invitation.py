import secrets
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone ,timedelta

class Invitation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    role_id: int = Field(foreign_key="roles.roles_id")
    token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        index=True,
        unique=True,
        nullable=False
    )
    is_used: bool = Field(default=False)
    expires_at: datetime = Field(
         default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=True), 
        nullable=False
    )
     