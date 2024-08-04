from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from typing import List, Optional
from models.person import Person, PersonFilm, Film
from db.elastic import get_elastic

import logging

class PersonService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search_persons(self, query: str) -> List[Person]:
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
                                  ))
            return films
        except NotFoundError:
            logging.error(f"Films not found for person id: {person_id}")
            return []

@lru_cache()
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(elastic)
