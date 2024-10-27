from uuid import UUID

from pydantic import BaseModel, conint


class LikeRequest(BaseModel):
    user_id: UUID
    item_id: UUID
    score: conint(ge=0, le=10)


class ReviewRequest(BaseModel):
    user_id: UUID
    item_id: UUID
    rating: conint(ge=0, le=100)
    comment: str


class FavoriteRequest(BaseModel):
    user_id: UUID
    item_id: UUID
