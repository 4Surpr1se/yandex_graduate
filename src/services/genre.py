from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel

from fastapi import Depends, Request, HTTPException
from starlette.datastructures import QueryParams

from db.abstract_storage import AbstractCache, AbstractDataStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base_service import BaseSingleItemService, BasePluralItemsService, ItemsModel


class GenreService(BasePluralItemsService):
  
    def __init__(self, cache: AbstractCache, storage: AbstractDataStorage):
        super().__init__(cache, storage)
        self.index = 'genres'
        self.model: BaseModel = Genre
        self.service_name = 'genres'

    def _generate_body(self, query_params: QueryParams = None) -> dict:
        size = int(query_params.get("size", 10000))
        body = {
            "query": {"match_all": {}},
            "size": size
        }
        return body

    async def get_items(self, request: Request, query_params: QueryParams = None) -> Optional[ItemsModel]:
        roles = await self.get_roles(request)


        if not roles:
            raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                                detail='Not allowed for unauthorized users')


        return await super().get_items(query_params=query_params)


@lru_cache()
def get_genre_service(
        cache: AbstractCache = Depends(get_redis),
        storage: AbstractDataStorage = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, storage)
