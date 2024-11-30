from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class FilmPriceRequest(BaseModel):
    film_id: str
    country: str 


class SubscriptionPriceRequest(BaseModel):
    subscription_type: str
    country: str


class TaxRateRequest(BaseModel):
    country: str
    name: str
    rate: float


class DiscountRequest(BaseModel):
    item_id: UUID
    name: str
    type: Literal['percentage', 'fixed']
    value: float
    start_date: str
    end_date: str