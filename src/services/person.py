import hashlib
import json
import logging
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from redis.asyncio import Redis

from db.elastic import ElasticInter, get_elastic
from db.redis import RedisInter, get_redis
from models.person import Film, Person

from .films import FilmsService

PERSONS_CACHE_EXPIRE_IN_SECONDS = 60


class FilmsByPersonId(FilmsService):
    def _generate_body(self, query_params: QueryParams, person_id: str) -> dict:
        page_size = int(query_params.get("page_size", 50))
        page_number = int(query_params.get("page_number", 1))
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


class PersonService(ElasticInter, RedisInter):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "persons"

    async def search_persons(self, query: str) -> List[Person]:
        cache = self._generate_cache("search_persons", query=query)
        persons = await self._get_persons_from_cache(cache)
        if not persons:
            persons = await self._search_persons_from_elastic(query)
            if not persons:
                return []
            await self._put_persons_to_cache(cache, persons)
        return persons

    async def _search_persons_from_elastic(self, query: str) -> List[Person]:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["full_name"]
                }
            }
        }
        logging.info(f"Elasticsearch query for persons: {body}")
        hits = await self._get_hits_from_elastic(body)
        persons = [Person(uuid=hit["_id"],
                          full_name=hit["_source"]["full_name"],
                          films=hit["_source"]["films"])
                   for hit in hits]
        return persons or None

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        cache = self._generate_cache("get_person_by_id", person_id=person_id)
        person = await self._get_person_from_cache(cache)
        if not person:
            person = await self._get_person_by_id_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(cache, person)
        return person

    async def _get_person_by_id_from_elastic(self, person_id: str) -> Optional[Person]:
        logging.info(f"Getting person by id: {person_id}")
        person = await self._get_by_id_from_elastic(id=person_id)
        return Person(uuid=person["id"], **person)

    async def get_films_by_person_id(self, query_params: QueryParams, person_id: str) -> List[Film]:
        films_by_person = FilmsByPersonId(self.redis, self.elastic)
        films = await films_by_person._get_films_from_elastic(query_params, person_id=person_id)
        return films.root

    # Cache methods
    def _generate_cache(self, method: str, **kwargs) -> str:
        query_str = json.dumps(kwargs, sort_keys=True)
        key = f"{method}:{query_str}"
        return hashlib.sha256(key.encode()).hexdigest()

    async def _get_persons_from_cache(self, cache: str) -> Optional[List[Person]]:
        persons = await self._get_from_cache(cache)
        return [Person.parse_raw(person) for person in json.loads(persons)] \
            if persons else None

    async def _put_persons_to_cache(self, cache: str, persons: List[Person]):
        await self._put_to_cache(cache, json.dumps([person.json() for person in persons]), PERSONS_CACHE_EXPIRE_IN_SECONDS)

    async def _get_person_from_cache(self, cache: str) -> Optional[Person]:
        person = await self._get_from_cache(cache)
        return Person.parse_raw(person) if person else None

    async def _put_person_to_cache(self, cache: str, person: Person):
        await self._put_to_cache(cache, person.json(), PERSONS_CACHE_EXPIRE_IN_SECONDS)


@ lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(redis, elastic)
