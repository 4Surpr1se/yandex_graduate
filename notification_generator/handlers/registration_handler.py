import uuid
import requests
from jinja2 import Template
from datetime import datetime
from pathlib import Path
from base_handler import BaseHandler
from schemas.notification import Notification, ChannelType, NotificationType


class RegistrationHandler(BaseHandler):
    def __init__(self, api_url, email_sender):
        self.api_url = api_url
        self.email_sender = email_sender
        self.template_path = Path("registration_email_template.html")

    def load_email_template(self, username):
        with open(self.template_path, "r") as file:
            template_content = file.read()
        template = Template(template_content)
        return template.render(username=username)

    def handle(self, message):
        user_id = message.get("user_id")
        email = message.get("email")
        username = message.get("username", "User")

        email_body = self.load_email_template(username)
        
        notification = Notification(
            title="Добро пожаловать в Practix",
            body=email_body,
            channel_type=ChannelType.EMAIL,
            message_type=NotificationType.REGISTRATION,
            content_id=uuid.uuid4(),
            recipients=[email]
        )

        self.send_notification(notification)

    def send_notification(self, notification: Notification):
        try:
            response = requests.post(
                self.api_url,
                json=notification.dict(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"Notification sent successfully to {notification.recipients}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send notification: {e}")