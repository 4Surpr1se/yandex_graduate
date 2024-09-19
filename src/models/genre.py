from typing import Optional

from pydantic import UUID4, BaseModel, model_validator


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
