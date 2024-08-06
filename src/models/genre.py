from typing import Optional

from pydantic import UUID4, BaseModel, Field


class GenreBase(BaseModel):
    uuid: UUID4
    name: str


class Genre(GenreBase):
    description: Optional[str] = None
