from handlers.base_handler import BaseNotificationHandler
from db import db
import logging
import json

class SMSNotificationHandler(BaseNotificationHandler):
    def __init__(self, sms_client):
        self.sms_client = sms_client 

    def send_sms(self, to, body, notification_id):
        raise NotImplementedError("Sms notifications not supported")

    def send(self, data):
        body = data.get("body", "")
        recipient = data.get("recipient")
        notification_id = data.get("notification_id")
        
        self.send_sms(recipient, body, notification_id)