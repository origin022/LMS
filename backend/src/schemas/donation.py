from pydantic import BaseModel
from uuid import UUID

class DonationCreate(BaseModel):
    amount: float

class DonationResponse(BaseModel):
    payment_url: str
    donation_id: UUID

class DonationCallbackResponse(BaseModel):
    message: str
    status: str
    donation_id: str