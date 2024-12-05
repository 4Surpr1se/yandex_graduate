import requests

from src.core.config import settings


def send_notification(user_mail: str):
    response = requests.post(
        settings.notification_service_url,
        json={
            'title': settings.notification_title,
            'body': settings.notification_body,
            'channel_type': settings.notification_channel_type,
            'message_type': settings.notification_type_billing,
            'recipients': [user_mail]
            }
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error sending mail")
