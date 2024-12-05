from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class PurchaseStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class FilmPurchase(Base):
    __tablename__ = "film_purchases"

    purchase_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(PurchaseStatus), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
