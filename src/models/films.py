from pydantic import BaseModel, model_validator, RootModel, UUID4
from typing import List


class Film(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: float

    @model_validator(mode='before')
    def rename_id_to_uuid(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        return values


class Films(RootModel):
    root: List[Film]