from pydantic import BaseModel


class CancelSubscriptionRequest(BaseModel):
    subscription_id: str


class FilmPaymentRequest(BaseModel):
    film_id: str
    country: str


class SubscriptionPaymentRequest(BaseModel):
    subscription_type: str
    country: str