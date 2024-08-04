from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre
from db.elastic import get_elastic
from typing import List, Optional

class GenreService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_genres(self) -> Optional[List[Genre]]:
        try:
            res = await self.elastic.search(index='genres', body={"query": {"match_all": {}}})
            hits = res['hits']['hits']
            genres = [Genre(uuid=hit['_id'], name=hit['_source']['name']) for hit in hits]
            return genres
        except NotFoundError:
            return None

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        try:
            res = await self.elastic.get(index='genres', id=genre_id)
            return Genre(uuid=res['_id'], name=res['_source']['name'])
        except NotFoundError:
            return None

@lru_cache()
def get_genre_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreService:
    return GenreService(elastic)
