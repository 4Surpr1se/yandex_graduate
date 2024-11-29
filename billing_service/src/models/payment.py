from sqlalchemy import TIMESTAMP, Column, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base
from src.extras.enums import Transaction_Status, Transaction_Type


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(Transaction_Status), nullable=False)
    type = Column(Enum(Transaction_Type), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
