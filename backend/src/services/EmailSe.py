from redmail import gmail
from src.core.config import config 
from datetime import datetime, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.models.User import User
from src.models.VerificationTok import VerificationToken

class EmailService:
    @staticmethod
    def _setup_gmail():
        gmail.username = config.MAIL_USERNAME
        gmail.password = config.MAIL_PASSWORD
        gmail.host = config.MAIL_SERVER
        gmail.port = config.MAIL_PORT
        gmail.set_template_paths(html="src/templates")



    @staticmethod
    def send_universal_mail(to_email: str, token: str, subject: str, template: str, route: str):
       
        EmailService._setup_gmail()
        
        magic_link = f"http://localhost:3000/{route}?token={token}"
        
        gmail.send(
            subject=subject,
            receivers=[to_email],
            html_template=template,
            body_params={
                "link": magic_link
            }
        )
    @staticmethod
    async def verify_user_email(token: str, db: AsyncSession):
        statement = select(VerificationToken).where(VerificationToken.token == token)
        result = await db.exec(statement)
        token_record = result.first()

        if not token_record:
            raise HTTPException(status_code=400, detail="الرابط غير صحيح")
        
        current_time_naive = datetime.now(timezone.utc).replace(tzinfo=None)

        if token_record.expires_at < current_time_naive:
            await db.delete(token_record)
            await db.commit()
            raise HTTPException(status_code=400, detail="الرابط منتهي الصلاحية")


        user_statement = select(User).where(User.email == token_record.email)
        user_result = await db.exec(user_statement)
        user = user_result.first()

        if not user:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")

        if user.roles_id == 4: 
            user.state_id = 1
            msg = "تم تفعيل حسابك كطالب بنجاح!"
        elif user.roles_id == 3:  
            user.state_id = 2
            msg = "تم تأكيد إيميلك، بانتظار موافقة المدير."
        else:
            user.state_id = 2
            msg = "تم تأكيد الإيميل."

        await db.delete(token_record)
        await db.commit()
        return {"message": msg, "state_id": user.state_id}