import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, Float, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SubscriptionStatus(enum.Enum):
    active = "active"
    cancelled = "cancelled"
    expired = "expired"

class TransactionStatus(enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"

class TransactionType(enum.Enum):
    subscription = "subscription"
    movie = "movie"

class PurchaseStatus(enum.Enum):
    paid = "paid"
    failed = "failed"

class DiscountType(enum.Enum):
    percentage = "percentage"
    fixed = "fixed"

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    subscription_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    status = Column(Enum(SubscriptionStatus, name='subscriptionstatus'), nullable=False)
    next_billing_date = Column(DateTime, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(TransactionStatus, name='transaction_status'), nullable=False)
    type = Column(Enum(TransactionType, name='transaction_type'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=True)

class FilmPurchase(Base):
    __tablename__ = "film_purchases"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    movie_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    status = Column(Enum(PurchaseStatus, name='purchase_status'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Discount(Base):
    __tablename__ = "discounts"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    item_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(DiscountType, name='discount_type'), nullable=False)
    value = Column(Numeric(5, 2), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class FilmPrice(Base):
    __tablename__ = "film_prices"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    item_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)

class TaxRate(Base):
    __tablename__ = "tax_rates"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    country = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    rate = Column(Float, nullable=False)