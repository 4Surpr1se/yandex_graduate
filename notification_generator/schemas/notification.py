from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from uuid import UUID

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