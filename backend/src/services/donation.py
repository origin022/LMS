import httpx
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.Donation import Donation, PaymentStatus
from jose import jwt, JWTError
from src.core.config import config
import time
import asyncio


class DonationService:

    CLIENT_ID = config.ZAINCASH_CLIENT_ID
    CLIENT_SECRET = config.ZAINCASH_CLIENT_SECRET
    BASE_URL = config.ZAINCASH_BASE_URL

    _cached_token = None
    _token_expires_at = 0
    _lock = asyncio.Lock()



    @staticmethod
    async def get_access_token():
        current_time = time.time()

        if DonationService._cached_token and current_time < (DonationService._token_expires_at - 120):
            return DonationService._cached_token

        async with DonationService._lock:
            current_time = time.time()
            if DonationService._cached_token and current_time < (DonationService._token_expires_at - 120):
                return DonationService._cached_token

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{DonationService.BASE_URL}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": DonationService.CLIENT_ID,
                        "client_secret": DonationService.CLIENT_SECRET,
                        "scope": "payment:read payment:write reverse:write"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    print(f"Auth Error: {response.text}")
                    raise HTTPException(status_code=400, detail="فشل الحصول على التوكن")
                
                data = response.json()
                
                DonationService._cached_token = data["access_token"]
                DonationService._token_expires_at = current_time + data["expires_in"]
                
                return DonationService._cached_token
    @staticmethod
    async def create_payment_request(amount: float, db: AsyncSession):

        new_donation = Donation(
            amount=amount,
            status=PaymentStatus.PENDING
        )

        db.add(new_donation)
        await db.commit()
        await db.refresh(new_donation)

        token = await DonationService.get_access_token()

        payload = {

            "language": "en",

            "externalReferenceId": str(new_donation.donation_id),

            "orderId": f"ORDER-{str(new_donation.donation_id)[:8]}",

            "amount": {
                "value": str(int(amount)),
                "currency": "IQD"
            },

            "customer": {
                "phone": "9647802999569"
            },

            "serviceType": "Delivery",

            "redirectUrls": {
                "successUrl": f"{config.API_URL}/api/v1/donations/callback",
                "failureUrl": f"{config.API_URL}/api/v1/donations/callback"
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:

            response = await client.post(
                f"{DonationService.BASE_URL}/api/v2/payment-gateway/transaction/init",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )

        print("Status:", response.status_code)
        print("ZainCash Response:", response.text)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=response.text)

        result = response.json()

        transaction_id = result["transactionDetails"]["transactionId"]

        new_donation.provider_transaction_id = transaction_id

        db.add(new_donation)
        await db.commit()
        await db.refresh(new_donation)

        return {
            "payment_url": result["redirectUrl"],
            "donation_id": str(new_donation.donation_id)
        }

    @staticmethod
    async def verify_zaincash_callback(token: str, db: AsyncSession):

        try:

            decoded = jwt.decode(
                token,
                DonationService.CLIENT_SECRET,
                algorithms=["HS256"]
            )

            event_data = decoded.get("data", {})

            transaction_id = event_data.get("transactionId")
            status = event_data.get("currentStatus")

            statement = select(Donation).where(
                Donation.provider_transaction_id == transaction_id
            )

            result = await db.exec(statement)
            donation = result.first()

            if not donation:
                raise HTTPException(status_code=404, detail="العملية غير موجودة")

            if status == "SUCCESS":
                donation.status = PaymentStatus.SUCCESS
            elif status == "FAILED":
                donation.status = PaymentStatus.FAILED
            else:
                donation.status = PaymentStatus.PENDING

            db.add(donation)
            await db.commit()
            await db.refresh(donation)

            return {
                "message": "تم تحديث الحالة",
                "status": donation.status,
                "donation_id": str(donation.donation_id)
            }

        except JWTError:
            raise HTTPException(status_code=400, detail="JWT غير صالح")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))