from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from src.core.dep import get_session
from src.schemas.donation import DonationCreate, DonationResponse
from src.services.donation import DonationService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.security import limiter, SENSITIVE_LIMIT, DEFAULT_LIMIT

router = APIRouter(prefix="/donations", tags=["Donations"])

@router.post("/start", response_model=DonationResponse)
@limiter.limit(SENSITIVE_LIMIT)
async def start_donation(request: Request, data: DonationCreate, db: AsyncSession  = Depends(get_session)):
    return await DonationService.create_payment_request(data.amount, db)

@router.get("/callback")
@limiter.limit(DEFAULT_LIMIT)
async def payment_callback(request: Request, token: str, db: AsyncSession = Depends(get_session)):
    result = await DonationService.verify_zaincash_callback(token, db)
    return RedirectResponse(
        url=f"http://localhost:5173/payment-status?status={result['status']}&donation_id={result['donation_id']}"
    )