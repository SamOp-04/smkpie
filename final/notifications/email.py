import smtplib
from email.message import EmailMessage
from core.config import settings

def send_email_alert(to: str, prediction: float):
    msg = EmailMessage()
    msg.set_content(f"Anomaly detected! Score: {prediction}")
    msg["Subject"] = "Security Alert"
    msg["From"] = settings.EMAIL_SENDER
    msg["To"] = to
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)