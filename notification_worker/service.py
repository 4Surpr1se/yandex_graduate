import json
import asyncio
import logging
from handlers import EmailNotificationHandler, PushNotificationHandler
from config import settings

class NotificationService:
    def __init__(self):
        self.handlers = {
            "email": EmailNotificationHandler(api_key=settings.sendinblue_api_key),
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
            logging.info(f"No handler for notification type: {notification_type}")
