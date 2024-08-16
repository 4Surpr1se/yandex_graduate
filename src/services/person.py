from functools import lru_cache
from typing import Optional
from pydantic import BaseModel

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import BaseSingleItemService, BasePluralItemsService, ItemsModel
from models.person import Person

from .films import FilmsService


class FilmsByPersonId(FilmsService):
    def _generate_body(self, query_params: QueryParams) -> dict:
        page_size = int(query_params.get("page_size", 50))
        page_number = int(query_params.get("page_number", 1))
        person_id = query_params.get('person_id')
        body = {
            "sort": [
                {
                    "imdb_rating": {"order": "desc" if query_params.get("sort", "-imdb_rating") == "-imdb_rating" else "asc"},
                }
            ],
            "size": page_size,
            "from": (page_number - 1) * page_size,
            "query": {
                "bool": {
                    "should": [
                        {"nested": {
                            "path": "directors",
                            "query": {"term": {"directors.id": person_id}}
                        }},
                        {"nested": {
                            "path": "actors",
                            "query": {"term": {"actors.id": person_id}}
                        }},
                        {"nested": {
                            "path": "writers",
                            "query": {"term": {"writers.id": person_id}}
                        }}
                    ]
                }
            }
        }
        return body


class PersonService(BaseSingleItemService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = 'persons'
        self.model: BaseModel = Person
        self.service_name = 'persons'

    async def get_films_by_person_id(self, query_params: QueryParams, person_id: str) -> Optional[ItemsModel]:
        query_params = QueryParams(**query_params, person_id=person_id)
        films_by_person = FilmsByPersonId(self.redis, self.elastic)
        films = await films_by_person.get_items(query_params)
        return films.root


@ lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(redis, elastic)
