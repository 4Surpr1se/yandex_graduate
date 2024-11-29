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
    transaction_type: str = Transaction_Type.subscription

    class Config:
        arbitrary_types_allowed = True
