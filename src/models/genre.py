from pydantic import BaseModel, UUID4, Field
from typing import Optional


class GenreBase(BaseModel):
    uuid: UUID4
    name: str


class Genre(GenreBase):
    description: Optional[str] = None
