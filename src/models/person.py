from typing import List, Literal

from pydantic import UUID4, BaseModel, model_validator


class PersonBase(BaseModel):
    uuid: UUID4
    full_name: str


class PersonFilm(BaseModel):
    uuid: UUID4
    roles: List[Literal['actor', 'writer', 'director']] = []

    @model_validator(mode='before')
    @classmethod
    def rename_fields(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        return values


class Person(PersonBase):
    films: List[PersonFilm] = []


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    roles: List[str]
