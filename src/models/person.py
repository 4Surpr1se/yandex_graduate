from pydantic import BaseModel, UUID4, Field
from typing import List, Literal


class Person(BaseModel):
    uuid: UUID4 = Field(alias="id")
    full_name: str = Field(alias="name")


class FilmPersonRole(BaseModel):
    uuid: UUID4 = Field(alias="id")
    roles: List[Literal['actor', 'writer', 'director']] = []


class PersonDetail(Person):
    films: List[FilmPersonRole] = []
