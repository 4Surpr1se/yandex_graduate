import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config import settings
from db import db
import logging
import json

class NotificationHandler:
    def send(self, data):
        raise NotImplementedError("Must override send method")
    
class PushNotificationHandler(NotificationHandler):
    async def send(self, data, websocket):
        await websocket.send(json.dumps(data))
        notification_id = data.get("notification_id")
        if notification_id:
            db.update_last_notification_send(notification_id)


class EmailNotificationHandler(NotificationHandler):
    def __init__(self, api_key, all_users_email_list=None):
        self.api_key = api_key
        self.all_users_email_list = all_users_email_list or []

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_email(self, to, subject, body, notification_id):
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to}],
            sender={"email": settings.email_sender},
            subject=subject,
            text_content=body
        )

        try:
            response = self.api_instance.send_transac_email(email)
            logging.info(f"Email sent to {to}. Response: {response}")
            db.update_last_notification_send(notification_id)
        except ApiException as e:
            logging.info(f"Failed to send email to {to}: {str(e)}")

    def send(self, data):
        subject = data.get("subject", "No Subject")
        body = data.get("body", "")
        recipient = data.get("recipient")
        notification_id = data.get("notification_id")

        if recipient == "all_users":
            for email in self.all_users_email_list:
                self.send_email(email, subject, body, notification_id)
        else:
            self.send_email(recipient, subject, body, notification_id)