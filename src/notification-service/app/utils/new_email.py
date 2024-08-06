import os
from email.message import EmailMessage

import aiosmtplib

from app.utils.logger import logger

smtp_server = "smtp.gmail.com"
sender_email = os.getenv("EMAIL_SENDER_MAIL", "")  # Enter your address
password = os.getenv("EMAIL_SECRET_KEY", "")


async def send_email_async(body: str, to_email: str) -> None:
    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = "Task Manager Notification"
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=587,
            start_tls=True,
            username=sender_email,
            password=password,
        )
        logger.info("Email sent")
    except aiosmtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")
