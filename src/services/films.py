import hashlib
import json
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from pydantic import BaseModel, RootModel
from redis.asyncio import Redis

from db.elastic import ElasticInter, get_elastic
from db.redis import RedisInter, get_redis

FILMS_CACHE_EXPIRE_IN_SECONDS = int(60 * 0.5)


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class Films(RootModel):
    root: List[Film]


class FilmsService(ElasticInter, RedisInter):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = 'movies'

    async def get_films(self, query_params: QueryParams) -> Optional[Films]:
        cache = self._generate_cache(query_params)
        films = await self._get_films_from_cache(cache)
        if not films:
            films = await self._get_films_from_elastic(query_params)
            if not films:
                return None
            await self._put_films_to_cache(cache, films)
        return films

    async def _get_films_from_elastic(self, query_params: QueryParams, **args) -> Optional[Films]:
        body = self._generate_body(query_params, **args)
        if not body:
            return None
        hits = await self._get_hits_from_elastic(body)
        films = [Film(uuid=hit['_id'], title=hit['_source']['title'],
                      imdb_rating=hit['_source']['imdb_rating']) for hit in hits]
        return Films(root=films) if films else None

    async def _get_films_from_cache(self, cache: str) -> Optional[Films]:
        films = await self._get_from_cache(cache)
        return Films.parse_raw(films) if films else None

    async def _put_films_to_cache(self, cache: str, films: Films):
        await self._put_to_cache(cache, films.json(), FILMS_CACHE_EXPIRE_IN_SECONDS)

    def _path_for_cache(self):
        return 'films'

    def _generate_cache(self, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items()))
        path = self._path_for_cache()
        key = f'{path}:{query_str}'
        return hashlib.sha256(key.encode()).hexdigest()

    def _generate_body(self, query_params: QueryParams) -> dict:
        page_size = int(query_params.get('page_size', 50))
        page_number = int(query_params.get('page_number', 1))
        genre_id = query_params.get('genre')
        body = {
            'sort': [
                {
                    'imdb_rating': {'order': 'desc' if query_params.get('sort', '-imdb_rating') == '-imdb_rating' else 'asc'},
                }
            ],
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'bool': {
                            'must': [
                                {'match': {'genres.id': genre_id}}
                            ]
                        }
                    }
                }
            } if genre_id else {'match_all': {}}
        }
        return body


@lru_cache()
def get_films_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsService:
    return FilmsService(redis, elastic)
