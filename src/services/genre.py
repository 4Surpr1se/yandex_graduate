from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre
from db.elastic import get_elastic
from typing import List

class GenreService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_all_genres(self) -> List[Genre]:
        try:
            res = await self.elastic.search(index="genres", body={"query": {"match_all": {}}})
            genres = [Genre(uuid=hit['_id'], name=hit['_source']['name']) for hit in res['hits']['hits']]
            return genres
        except NotFoundError:
            return []

    async def get_genre_by_id(self, genre_id: str) -> Genre:
        try:
            res = await self.elastic.get(index="genres", id=genre_id)
            return Genre(uuid=res['_id'], name=res['_source']['name'])
        except NotFoundError:
            return None

@lru_cache()
def get_genre_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreService:
    return GenreService(elastic)
