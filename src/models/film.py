from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Literal
from datetime import datetime
from genre import GenreInFilm
from person import Person


class Film(BaseModel):
    uuid: UUID4 = Field(alias="id")
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = Field(None, ge=0, le=10)
    genres: List[GenreInFilm] = []
    actors: List[Person] = []
    directors: List[Person] = []
    writers: List[Person] = []
