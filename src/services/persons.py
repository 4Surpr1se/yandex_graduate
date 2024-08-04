from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.person import Person, PersonFilm
from db.elastic import get_elastic
from typing import List, Optional

class PersonService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search_persons(self, query_params: dict) -> Optional[List[Person]]:
        try:
            body = {
                "query": {
                    "multi_match": {
                        "query": query_params.get("query", ""),
                        "fields": ["full_name"]
                    }
                }
            }
            res = await self.elastic.search(index='persons', body=body)
            hits = res['hits']['hits']
            persons = [
                Person(
                    uuid=hit['_id'],
                    full_name=hit['_source']['full_name'],
                    films=[{"uuid": film["uuid"], "roles": film["roles"]} for film in hit['_source']['films']]
                ) for hit in hits
            ]
            return persons
        except NotFoundError:
            return None

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        try:
            res = await self.elastic.get(index='persons', id=person_id)
            return Person(
                uuid=res['_id'],
                full_name=res['_source']['full_name'],
                films=[{"uuid": film["uuid"], "roles": film["roles"]} for film in res['_source']['films']]
            )
        except NotFoundError:
            return None

    async def get_person_films(self, person_id: str) -> Optional[List[PersonFilm]]:
        try:
            res = await self.elastic.get(index='persons', id=person_id)
            films = [
                PersonFilm(uuid=film["uuid"], title=film["title"], imdb_rating=film["imdb_rating"])
                for film in res['_source']['films']
            ]
            return films
        except NotFoundError:
            return None

@lru_cache()
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(elastic)
