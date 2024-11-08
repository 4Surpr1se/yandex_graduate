from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uuid
from message_sender import send_message

app = FastAPI()


class ChannelType(Enum):
    EMAIL = 1
    BROWSER = 2


class Notification(BaseModel):
    title: str
    body: str
    channel_type: ChannelType
    recipients: List[str]
    usernames: Optional[List[str]] = None


@app.post("/notify/send-notification")
async def send_notification(notification: Notification):
    """
    Универсальный маршрут для отправки уведомлений.
    Использует channel_type и список usernames для персонализации сообщений.
    """
    headers = {"X-Request-Id": str(uuid.uuid4())}

    if notification.recipients != ["all-users"] and notification.usernames:
        if len(notification.recipients) != len(notification.usernames):
            raise HTTPException(status_code=400, detail="Number of usernames must match number of recipients")

    if notification.recipients == ["all-users"]:
        message_body = f"""
            <html>
            <body>
                <h1>{notification.title}</h1>
                <p>{notification.body}</p>
            </body>
            </html>
        """
        queue_name = "emails.send-mass-email" if notification.channel_type == ChannelType.EMAIL else \
            "browser.send-mass-notification"
        send_message(queue_name, message_body, headers=headers)
        return {"status": f"Mass {'email' if notification.channel_type == ChannelType.EMAIL else 'browser'} "
                          f"notification sent to all users"}

    for index, recipient in enumerate(notification.recipients):
        username = notification.usernames[index] if notification.usernames else "User"
        personalized_body = f"""
            <html>
            <body>
                <h1>{notification.title}</h1>
                <p>Hello {username},</p>
                <p>{notification.body}</p>
            </body>
            </html>
        """
        headers["Recipient"] = recipient
        queue_name = "emails.send-individual" if notification.channel_type == ChannelType.EMAIL \
            else "browser.send-individual"
        send_message(queue_name, personalized_body, headers=headers)

    return {"status": "Individual messages sent"}
