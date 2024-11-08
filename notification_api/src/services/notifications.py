from src.models.notification import NotificationModel
from src.schemas.notification import Notification
from src.extras.enums import NotificationType
from src.services.message_queue import MessageQueueService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import uuid4


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.message_queue = MessageQueueService()

    async def add_notification(self, notification: Notification):
        new_notification = NotificationModel(
            notification_id=uuid4(),
            content_id=notification.content_id,
            last_update=datetime.utcnow(),
            is_sent=False
        )
        self.db.add(new_notification)
        await self.db.commit()

    def send_notification_to_queue(self, notification: Notification):
        headers = {
            "X-Request-Id": str(uuid4()),
            "channel_type": str(notification.channel_type.value)
        }

        if notification.recipients == ["all-users"]:
            message_body = (f"<html><body>"
                            f"<h1>{notification.title}</h1>"
                            f"<p>{notification.body}</p>"
                            f"</body></html>")
            self.message_queue.send_message("emails.send-mass-email", message_body, headers)
        else:
            for index, recipient in enumerate(notification.recipients):
                username = notification.usernames[index] if notification.usernames else "User"
                personalized_body = \
                    (f"<html><body>"
                     f"<h1>{notification.title}</h1>"
                     f"<p>Hello {username},</p>"
                     f"<p>{notification.body}</p>"
                     f"</body></html>")
                headers["Recipient"] = recipient
                queue_name = "emails.send-welcome" \
                    if notification.message_type == NotificationType.REGISTRATION else \
                             "emails.send-weekly-films" \
                    if notification.message_type == NotificationType.WEEKLY_REPORT else \
                             "emails.send-individual"
                self.message_queue.send_message(queue_name, personalized_body, headers)
