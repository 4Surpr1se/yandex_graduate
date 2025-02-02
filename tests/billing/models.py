from sqlalchemy import TIMESTAMP, Column, Enum, Float, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import Base

import enum


class PaymentMethod(object):
    BANK_CARD = "bank_card"
    SBP = "spb"
    YOO_MONEY = "yoo_money"


class Subscription_Status(enum.Enum):
    active = "active"
    canceled = "canceled"
    expired = "expired"


class Transaction_Status(enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"


class Transaction_Type(enum.Enum):
    subscription = "subscription"
    movie = "movie"


class PurchaseStatus(enum.Enum):
    PAID = "paid"
    FAILED = "failed"


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
