from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, model_validator


class GenreBase(BaseModel):
    uuid: UUID4
    full_name: str

    @model_validator(mode='before')
    @classmethod
    def rename_fields(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        if 'name' in values:
            values['full_name'] = values.pop('name')
        return values

    class Config:
        populate_by_name = True


class PersonBase(BaseModel):
    uuid: UUID4
    full_name: str

    @model_validator(mode='before')
    @classmethod
    def rename_fields(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        if 'name' in values:
            values['full_name'] = values.pop('name')
        return values

    class Config:
        populate_by_name = True


class Film(BaseModel):
    uuid: UUID4
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = Field(None, ge=0, le=10)
    genres: List[GenreBase] = []
    actors: List[PersonBase] = []
    directors: List[PersonBase] = []
    writers: List[PersonBase] = []

    @model_validator(mode='before')
    @classmethod
    def rename_fields(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        return values

    class Config:
        populate_by_name = True
