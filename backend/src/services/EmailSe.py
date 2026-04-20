from redmail import gmail
from src.core.config import config 
from datetime import datetime, timezone
from src.models.Profile import Profile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.models.User import User
from src.models.VerificationTok import VerificationToken
import asyncio 

class EmailService:
    @staticmethod
    def _setup_gmail():
        gmail.username = config.MAIL_USERNAME
        gmail.password = config.MAIL_PASSWORD
        gmail.host = config.MAIL_SERVER
        gmail.port = config.MAIL_PORT
        gmail.set_template_paths(html="src/templates")

    @staticmethod
    async def send_universal_mail(to_email: str, token: str, subject: str, template: str, route: str):
        EmailService._setup_gmail()
        
        # Build base URL carefully to avoid localhost issues or double slashes
        base_url = config.API_URL.rstrip("/")
        if "/api/v1" not in base_url:
            base_url = f"{base_url}/api/v1"
            
        magic_link = f"{base_url}/{route}?token={token}"
        
        gmail.send(
            subject=subject,
            receivers=[to_email],
            html_template=template,
            body_params={"link": magic_link}
        )
    @staticmethod
    async def verify_user_email(token: str, db: AsyncSession):
        statement = select(VerificationToken).where(VerificationToken.token == token)
        result = await db.exec(statement)
        token_record = result.first()

        if not token_record:
            raise HTTPException(status_code=400, detail="الرابط غير صحيح")

        token_expiry = token_record.expires_at
        current_time = datetime.now(timezone.utc)

        if token_expiry.replace(tzinfo=timezone.utc) < current_time:
            await db.delete(token_record)
            await db.commit()
            raise HTTPException(status_code=400, detail="الرابط منتهي الصلاحية")

        user_stmt = select(User).where(User.email == token_record.email)
        user_res = await db.exec(user_stmt)
        user = user_res.first()

        if not user:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")

        profile_stmt = select(Profile).where(Profile.user_id == user.user_id)
        profile_res = await db.exec(profile_stmt)
        profile = profile_res.first()

        if not profile:
            db.add(Profile(user_id=user.user_id))

        if user.roles_id == 4:
            user.state_id = 1
            msg = "تم تفعيل حسابك كطالب بنجاح!"
        else:
            user.state_id = 2
            msg = "تم تأكيد بريدك الإلكتروني، يرجى انتظار تفعيل الحساب من قبل الإدارة."

        await db.delete(token_record)
        await db.commit()
    
        await db.refresh(user)

        from fastapi.responses import RedirectResponse
        frontend_login = f"{config.FRONTEND_URL.rstrip('/')}/login?verified=true&role={user.roles_id}"
        return RedirectResponse(url=frontend_login)