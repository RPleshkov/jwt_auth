from email.message import EmailMessage

import aiosmtplib
from core.config import settings


async def send_confirmation_email(to_email: str, token: str):
    confirmation_url = f"{settings.frontend_url}/auth/register_confirm?token={token}"
    text = f"""Спасибо за регистрацию!  
Для подтверждения регистрации перейдите по ссылке: {confirmation_url}  
"""
    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.smtp.username
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"

    await aiosmtplib.send(
        message,
        hostname=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password.get_secret_value(),
        use_tls=True,
    )
