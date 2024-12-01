import json
import asyncio
import logging
from handlers.email_notification_handler import EmailNotificationHandler
from handlers.push_notification_handler import PushNotificationHandler
from handlers.sms_notification_handler import SMSNotificationHandler
from channel_enum import ChannelType

class NotificationService:
    def __init__(self):
        self.handlers = {
            ChannelType.EMAIL : EmailNotificationHandler(),
            ChannelType.BROWSER: PushNotificationHandler()
        }

    def register_handler(self, notification_type, handler):
        self.handlers[notification_type] = handler

    def process_message(self, message, properties, websocket=None):
        channel_id = None
        if properties.headers:
            try:
                channel_id = ChannelType(int(properties.headers.get('channel_type')))
            except (ValueError, KeyError):
                logging.warning(f"Invalid or missing channel_type in headers: {properties.headers}")

        handler = self.handlers.get(channel_id)

        if handler:
            if channel_id == ChannelType.BROWSER and websocket:
                asyncio.run(handler.send(message, properties, websocket))
            else:
                handler.send(message, properties)
        else:
            logging.info(f"No handler for notification type: {channel_id}")

