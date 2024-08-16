import hashlib
import json
from functools import lru_cache
from pydantic import BaseModel

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import BaseSingleItemService, BasePluralItemsService
from models.person import Person


class SearchPersonService(BasePluralItemsService):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = 'persons'
        self.model: BaseModel = Person
        self.service_name = 'persons'

    def _generate_cache(self, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items())) if query_params else ''
        key = f'{self.service_name}/search:{query_str}'
        cache_key = hashlib.sha256(key.encode()).hexdigest()
        return cache_key

    def _generate_body(self, query_params: QueryParams) -> dict:
        page_size = int(query_params.get('page_size', 50))
        page_number = int(query_params.get('page_number', 1))
        query = query_params.get('query', '')

        if query:
            search_query = {
                "multi_match": {
                    "query": query,
                    "fields": ["full_name"]
                }
            }
        else:
            search_query = {
                "match_all": {}
            }

        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            "query": search_query
        }

        return body


@ lru_cache()
def search_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> SearchPersonService:
    return SearchPersonService(redis, elastic)
