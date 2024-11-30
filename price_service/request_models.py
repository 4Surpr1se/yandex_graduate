from pydantic import BaseModel, Field


class FilmPriceRequest(BaseModel):
    film_id: str
    country: str 


class SubscriptionPriceRequest(BaseModel):
    subscription_type: str
    country: str