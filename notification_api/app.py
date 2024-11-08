from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from uuid import UUID
from message_sender import send_message

app = FastAPI()


class ChannelType(Enum):
    EMAIL = 1
    BROWSER = 2


class NotificationType(Enum):
    MASS_MAILING = 1
    WEEKLY_REPORT = 2
    REGISTRATION = 3


class Notification(BaseModel):
    title: str
    body: str
    channel_type: ChannelType
    message_type: NotificationType
    content_id: UUID
    recipients: List[str]
    usernames: Optional[List[str]] = None


@app.post("/notify/send-notification")
async def send_notification(notification: Notification):
    """
    Универсальный маршрут для отправки уведомлений.
    Использует channel_type, message_type и список usernames для персонализации сообщений.
    """
    headers = {"X-Request-Id": str(uuid.uuid4()),
               "channel_type": str(notification.channel_type.value)}

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
        send_message("email.send-mass-notification", message_body, headers=headers)
        return {"status": f"Mass notification sent to all users, channel type: {notification.channel_type.name}"}

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
        if notification.notification_type == NotificationType.REGISTRATION:
            send_message("email.send-welcome", personalized_body, headers=headers)
        elif notification.notification_type == NotificationType.WEEKLY_REPORT:
            send_message("email.send-weekly-films", personalized_body, headers=headers)
        else:
            send_message("email.send-individual", personalized_body, headers=headers)

    return {"status": "Individual message s sent"}
