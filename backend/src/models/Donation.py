from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Numeric  

class PaymentStatus(str, Enum):
    PENDING = "pending"  
    SUCCESS = "success"   
    FAILED = "failed"     
    CANCELLED = "cancelled" 

class Donation(SQLModel, table=True):
    donation_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    currency: str = Field(default="IQD", max_length=3)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    provider_transaction_id: Optional[str] = Field(default=None, index=True)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
 

    class Config:
        use_enum_values = True