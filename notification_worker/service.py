import json
import asyncio
from handlers import EmailNotificationHandler, PushNotificationHandler
from config import settings

class NotificationService:
    def __init__(self):
        self.handlers = {
            "email": EmailNotificationHandler(
                smtp_server=settings.smtp_server,
                smtp_port=settings.smtp_port,
                smtp_user=settings.smtp_user,
                smtp_password=settings.smtp_password
            ),
            "push": PushNotificationHandler(),
        }

    def register_handler(self, notification_type, handler):
        self.handlers[notification_type] = handler

    def process_message(self, message, websocket=None):
        data = json.loads(message)
        notification_type = data.get("type")
        handler = self.handlers.get(notification_type)

        if handler:
            if notification_type == "push" and websocket:
                asyncio.run(handler.send(data, websocket))
            else:
                handler.send(data)
        else:
            print(f"No handler for notification type: {notification_type}")
