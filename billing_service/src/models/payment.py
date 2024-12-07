from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base
from src.extras.enums import Subscription_Status, Transaction_Status, Transaction_Type


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(), nullable=False)
    base_price = Column(Float, nullable=False)
    base_currency = Column(String(3), nullable=False)


class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    __table_args__ = (
        UniqueConstraint('user_id', 'subscription_id', ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID, nullable=False)
    user_mail = Column(String(), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'))
    status = Column(Enum(Subscription_Status), nullable=False)
    next_billing_date = Column(TIMESTAMP)
    payment_method_id = Column(UUID)

    subscription = relationship("Subscription", backref="user_subscription")


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
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=True)

    subscription = relationship("Subscription", backref="transactions")
    

class FilmPurchase(Base):
    __tablename__ = "film_purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True) 
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
