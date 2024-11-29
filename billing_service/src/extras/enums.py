from enum import Enum


class PaymentMethod(object):
    BANK_CARD = "bank_card"
    SBP = "spb"
    YOO_MONEY = "yoo_money"


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"


class Transaction_Status(Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"


class Transaction_Type(Enum):
    subscription = "subscription"
    movie = "movie"


class PurchaseStatus(Enum):
    PAID = "paid"
    FAILED = "failed"
