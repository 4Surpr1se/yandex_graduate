from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from models.genre import GenreBase
from models.person import PersonBase


class Film(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: List[GenreBase] = []
    actors: List[PersonBase] = []
    directors: List[PersonBase] = []
    writers: List[PersonBase] = []
