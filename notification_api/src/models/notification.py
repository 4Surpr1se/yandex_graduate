from sqlalchemy import Column, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.db.base import Base
from uuid import uuid4
from datetime import datetime


class NotificationModel(Base):
    __tablename__ = "notifications"

    notification_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    content_id = Column(PG_UUID(as_uuid=True), nullable=True)
    last_update = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_notification_send = Column(TIMESTAMP, nullable=True)
    is_sent = Column(Boolean, default=False)
