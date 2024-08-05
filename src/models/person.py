from pydantic import BaseModel, UUID4, Field
from typing import List, Literal


class PersonBase(BaseModel):
    uuid: UUID4
    full_name: str


class PersonFilm(BaseModel):
    uuid: UUID4
    roles: List[Literal['actor', 'writer', 'director']] = []


class Person(PersonBase):
    films: List[PersonFilm] = []


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    roles: List[str]
