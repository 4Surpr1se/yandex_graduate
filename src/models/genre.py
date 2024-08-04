from pydantic import BaseModel, UUID4, Field
from typing import Optional


class GenreInFilm(BaseModel):
    uuid: UUID4 = Field(alias="id")
    name: str


class Genre(GenreInFilm):
    description: Optional[str] = None
