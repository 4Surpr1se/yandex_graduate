from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class FilmPurchase(Base):
    __tablename__ = "film_purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True) 
    transaction_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
