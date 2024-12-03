import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from handlers.base_handler import BaseNotificationHandler
from bs4 import BeautifulSoup
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
            
    def parse_html_data(self, data):
        try:
            decoded_data = data.decode("utf-8")
            soup = BeautifulSoup(decoded_data, "html.parser")

            subject = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Subject"
            body = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])
            return {"subject": subject, "body": body}
        except Exception as e:
            logging.error(f"Failed to parse HTML data: {e}")
            return {"subject": "No Subject", "body": ""}

    def send(self, data, properties) -> None:
        logging.info(f"data {data}")

        parsed_data = self.parse_html_data(data)
        subject = parsed_data["subject"]
        body = parsed_data["body"]

        recipient = properties.headers.get("Recipient")
        notification_id = properties.headers.get("X-Request-Id")

        if not recipient:
            logging.error("Recipient is missing in properties")
            return

        self.send_email(recipient, subject, body, notification_id)
        