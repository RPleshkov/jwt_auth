from email.message import EmailMessage
from celery import shared_task
from config import settings
import smtplib


@shared_task
def send_confirmation_email(to_email: str, token: str):
    confirmation_url = f"{settings.frontend_url}/auth/register_confirm?token={token}"
    text = f"""Спасибо за регистрацию!  
Для подтверждения регистрации перейдите по ссылке: {confirmation_url}  
"""
    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.email.username
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"

    with smtplib.SMTP_SSL(
        host=settings.email.host,
        port=settings.email.port,
    ) as smtp:
        smtp.login(
            user=settings.email.username,
            password=settings.email.password.get_secret_value(),
        )
        smtp.send_message(msg=message)
