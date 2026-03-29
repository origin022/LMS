from fastapi import APIRouter, Depends
from src.core.dep import get_session
from src.schemas.donation import DonationCreate, DonationResponse, DonationCallbackResponse
from src.services.donation import DonationService
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/donations", tags=["Donations"])

@router.post("/start", response_model=DonationResponse)
async def start_donation(data: DonationCreate, db: AsyncSession  = Depends(get_session)):
    return await DonationService.create_payment_request(data.amount, db)



@router.get("/callback", response_model=DonationCallbackResponse)
async def payment_callback(token: str, db: AsyncSession = Depends(get_session)):

    return await DonationService.verify_zaincash_callback(token, db)