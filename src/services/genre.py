from functools import lru_cache
from pydantic import BaseModel

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from starlette.datastructures import QueryParams

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base_service import BaseSingleItemService, BasePluralItemsService


class GenreService(BasePluralItemsService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
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


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(redis, elastic)
