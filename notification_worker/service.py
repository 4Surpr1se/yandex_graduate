import json
import asyncio
import logging
from handlers.email_notification_handler import EmailNotificationHandler
from handlers.push_notification_handler import PushNotificationHandler
from handlers.sms_notification_handler import SmsNotificationHandler

class NotificationService:
    def __init__(self):
        self.handlers = {
            "email": EmailNotificationHandler(),
            "push": PushNotificationHandler(),
            "sms": SmsNotificationHandler()
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
