from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from typing import List, Optional
import json
import hashlib

from models.person import Person, PersonFilm, Film
from db.elastic import get_elastic
from redis.asyncio import Redis

import logging

PERSONS_CACHE_EXPIRE_IN_SECONDS=60

class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def search_persons(self, query: str) -> List[Person]:
        cache = self._generate_cache('search_persons', query=query)
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
        try:
            res = await self.elastic.search(index="persons", body=body)
            logging.info(f"Elasticsearch response for persons: {res}")
            persons = []
            for hit in res['hits']['hits']:
                films = await self.get_films_by_person_id(hit['_id'])
                person = Person(
                    uuid=hit['_id'],
                    full_name=hit['_source']['full_name'],
                    films=[PersonFilm(uuid=film.uuid, roles=film.roles) for film in films]
                )
                persons.append(person)
            return persons
        except NotFoundError:
            logging.error(f"Person not found for query: {query}")
            return []

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        cache = self._generate_cache('get_person_by_id', person_id=person_id)
        person = await self._get_person_from_cache(cache)
        if not person:
            person = await self._get_person_by_id_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(cache, person)
        return person

    async def _get_person_by_id_from_elastic(self, person_id: str) -> Optional[Person]:
        logging.info(f"Getting person by id: {person_id}")
        try:
            res = await self.elastic.get(index="persons", id=person_id)
            logging.info(f"Elasticsearch response for person by id: {res}")
            films = await self.get_films_by_person_id(person_id)
            return Person(
                uuid=res['_id'],
                full_name=res['_source']['full_name'],
                films=[PersonFilm(uuid=film.uuid, roles=film.roles) for film in films]
            )
        except NotFoundError:
            logging.error(f"Person not found by id: {person_id}")
            return None

    async def get_films_by_person_id(self, person_id: str) -> List[Film]:
        logging.info(f"Getting films by person id: {person_id}")
        try:
            res = await self.elastic.search(index="movies", body={
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
            })
            logging.info(f"Elasticsearch response for films by person id: {res}")
            films = []
            for hit in res['hits']['hits']:
                roles = []
                for role in ['directors', 'actors', 'writers']:
                    for person in hit['_source'].get(role, []):
                        if person['id'] == person_id:
                            roles.append(role[:-1])
                films.append(Film(uuid=hit['_id'],
                                  title=hit['_source']['title'],
                                  imdb_rating=hit['_source']['imdb_rating'],
                                  roles=roles))
            return films
        except NotFoundError:
            logging.error(f"Films not found for person id: {person_id}")
            return []

    # Cache methods
    def _generate_cache(self, method: str, **kwargs) -> str:
        query_str = json.dumps(kwargs, sort_keys=True)
        key = f'{method}:{query_str}'
        return hashlib.sha256(key.encode()).hexdigest()

    async def _get_persons_from_cache(self, cache: str) -> Optional[List[Person]]:
        persons = await self.redis.get(cache)
        if not persons:
            return None
        return [Person.parse_raw(person) for person in json.loads(persons)]

    async def _put_persons_to_cache(self, cache: str, persons: List[Person]):
        await self.redis.set(cache, json.dumps([person.json() for person in persons]), PERSONS_CACHE_EXPIRE_IN_SECONDS)

    async def _get_person_from_cache(self, cache: str) -> Optional[Person]:
        person = await self.redis.get(cache)
        if not person:
            return None
        return Person.parse_raw(person)

    async def _put_person_to_cache(self, cache: str, person: Person):
        await self.redis.set(cache, person.json(), PERSONS_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(elastic)
