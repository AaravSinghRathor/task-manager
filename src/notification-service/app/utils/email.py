import os
import smtplib
import ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.getenv("EMAIL_SENDER_MAIL", '')  # Enter your address
password = os.getenv("EMAIL_SECRET_KEY", '')
message = """\
Subject: Task Manager Notification
This message is sent from task manager.

{}
"""


def send_email(receiver_email: str, message_body: str) -> bool:
    print(f"sending mail to user: {receiver_email} with message body: {message_body}")
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            err = server.sendmail(
                sender_email, receiver_email, message.format(message_body)
            )
            if err:
                print(err)
                return False
        return True
    except Exception as e:
        print(e)
        return False
