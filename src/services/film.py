from functools import lru_cache

from pydantic import BaseModel
from fastapi import Depends

from models.film import Film
from services.base_service import BaseSingleItemService
from db.abstract_storage import AbstractCache, AbstractDataStorage
from db.elastic import get_elastic
from db.redis import get_redis


class FilmService(BaseSingleItemService):
    def __init__(self, cache: AbstractCache, storage: AbstractDataStorage):
        super().__init__(cache, storage)
        self.index = 'movies'
        self.model: BaseModel = Film
        self.service_name = 'film'

        
@lru_cache()
def get_film_service(
        cache: AbstractCache = Depends(get_redis),
        storage: AbstractDataStorage = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, storage)
