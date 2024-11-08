from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from src.extras.enums import ChannelType, NotificationType


class Notification(BaseModel):
    title: str
    body: str
    channel_type: ChannelType
    message_type: NotificationType
    content_id: Optional[UUID] = None
    recipients: List[str]
    usernames: Optional[List[str]] = None
