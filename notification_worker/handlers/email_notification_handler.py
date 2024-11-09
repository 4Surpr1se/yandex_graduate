import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from handlers.base_handler import BaseNotificationHandler
from config import settings
from db import db
import logging

class EmailNotificationHandler(BaseNotificationHandler):
    def __init__(self, smtp_host=settings.smtp_host, smtp_port=settings.smtp_port):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_email(self, to: str, subject: str, body: str, notification_id: str) -> None:
        message = MIMEMultipart()
        message['From'] = settings.email_sender
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html')) 

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.sendmail(settings.email_sender, to, message.as_string())
            
            logging.info(f"Email sent to {to}")
            db.update_last_notification_send(notification_id)
        except Exception as e:
            logging.error(f"Failed to send email to {to}: {str(e)}")

    def send(self, data: dict) -> None:
        subject = data.get("subject", "No Subject")
        body = data.get("body", "")
        recipient = data.get("recipient")
        notification_id = data.get("notification_id")

        self.send_email(recipient, subject, body, notification_id)
        