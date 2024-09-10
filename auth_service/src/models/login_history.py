import uuid
from datetime import datetime


from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class UserLogin(Base):
    __tablename__ = 'user_login'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, user_id: UUID):
        self.user_id = user_id

    def __repr__(self):
        return f'Logged in at <{self.logged_at}>'

