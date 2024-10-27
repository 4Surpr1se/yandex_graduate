from uuid import UUID

from beanie import Document
from pydantic import Field, conint
from datetime import datetime

from src.models.mixin import BaseMixin


class Favorite(BaseMixin):
    user_id: UUID
    item_id: UUID


class Like(BaseMixin):
    user_id: UUID
    item_id: UUID
    score: conint(ge=0, le=10)


class Review(BaseMixin):
    user_id: UUID
    item_id: UUID
    rating: conint(ge=0, le=100)
    comment: str
