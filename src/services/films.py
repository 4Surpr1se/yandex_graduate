import hashlib
import json
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.datastructures import QueryParams
from pydantic import BaseModel, RootModel
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

FILMS_CACHE_EXPIRE_IN_SECONDS = int(60 * 0.5)


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float


class Films(RootModel):
    root: List[Film]


class FilmsService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films(self, query_params: QueryParams) -> Optional[Films]:
        cache = self._generate_cache('films', query_params)
        films = await self._get_films_from_cache(cache)
        if not films:
            films = await self._get_films_from_elastic(query_params)
            if not films:
                return None
            await self._put_films_to_cache(cache, films)
        return films

    async def _get_films_from_elastic(self, query_params: QueryParams) -> Optional[Films]:
        try:
            page_size = int(query_params.get('page_size', 50))
            page_number = int(query_params.get('page_number', 1))
            body = {
                'sort': [
                    {
                        'imdb_rating': {'order': 'desc' if query_params.get('sort', '-imdb_rating') == '-imdb_rating' else 'asc'},
                    }
                ],
                'size': page_size,
                'from': (page_number - 1) * page_size,
            }
            res = await self.elastic.search(index='movies', body=body)
            hits = res['hits']['hits']
            films = [Film(id=hit['_id'], title=hit['_source']['title'],
                          imdb_rating=hit['_source']['imdb_rating']) for hit in hits]
        except NotFoundError:
            return None
        return Films(root=films)

    async def _get_films_from_cache(self, cache: str) -> Optional[Films]:
        films = await self.redis.get(cache)
        if not films:
            return None
        return Films.parse_raw(films)

    async def _put_films_to_cache(self, cache: str, films: Films):
        await self.redis.set(cache, films.json(), FILMS_CACHE_EXPIRE_IN_SECONDS)

    def _generate_cache(self, path: str, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items()))
        key = f'{path}:{query_str}'
        return hashlib.sha256(key.encode()).hexdigest()


@lru_cache()
def get_films_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsService:
    return FilmsService(redis, elastic)
