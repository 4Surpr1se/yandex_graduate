import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base
from enum import Enum as PyEnum


class Provider(PyEnum):
    GOOGLE = "google"
    PASSWORD = "password"

class UserLogin(Base):
    __tablename__ = 'user_login'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)
    provider = Column(Enum(Provider), nullable=False)

    def __init__(self, user_id: UUID, provider: Provider):
        self.user_id = user_id
        self.provider = provider

    def __repr__(self):
        return f'Logged in at <{self.logged_at}> via {self.provider.value}'

