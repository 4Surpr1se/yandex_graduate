from uuid import UUID, uuid4

from pydantic import BaseModel
from yookassa.domain.models import Currency

from src.extras.enums import PaymentMethod, Transaction_Type


class RequestPayment(BaseModel):
    user_id: UUID
    amount: float
    currency: str
    description: str
    payment_method: str = "bank_card"

    class Config:
        arbitrary_types_allowed = True


class RequestSubscription(BaseModel):
    user_id: UUID
    subscription_id: UUID
    description: str
    payment_method: str = "bank_card"
