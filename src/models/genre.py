from typing import Optional

from pydantic import BaseModel, UUID4, model_validator


class GenreBase(BaseModel):
    uuid: UUID4
    name: str

    @model_validator(mode='before')
    def rename_id_to_uuid(cls, values):
        if 'id' in values:
            values['uuid'] = values.pop('id')
        return values


class Genre(GenreBase):
    description: Optional[str] = None
