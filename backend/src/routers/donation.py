from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from src.core.dep import get_session
from src.schemas.donation import DonationCreate, DonationResponse
from src.services.donation import DonationService
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/donations", tags=["Donations"])

@router.post("/start", response_model=DonationResponse)
async def start_donation(data: DonationCreate, db: AsyncSession  = Depends(get_session)):
    return await DonationService.create_payment_request(data.amount, db)

@router.get("/callback")
async def payment_callback(token: str, db: AsyncSession = Depends(get_session)):
    result = await DonationService.verify_zaincash_callback(token, db)
    return RedirectResponse(
        url=f"http://localhost:5173/payment-status?status={result['status']}&donation_id={result['donation_id']}"
    )