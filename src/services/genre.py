import hashlib
import json
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
import logging

from models.genre import Genre
from db.elastic import get_elastic
from db.redis import get_redis

GENRES_CACHE_EXPIRE_IN_SECONDS = 60 * 5

class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all_genres(self) -> List[Genre]:
        cache_key = self._generate_cache_key('get_all_genres')
        genres = await self._get_genres_from_cache(cache_key)
        if not genres:
            genres = await self._get_all_genres_from_elastic()
            if not genres:
                return []
            await self._put_genres_to_cache(cache_key, genres)
        return genres

    async def _get_all_genres_from_elastic(self) -> List[Genre]:
        try:
            res = await self.elastic.search(index="genres", body={"query": {"match_all": {}}})
            genres = [Genre(uuid=hit['_id'], name=hit['_source']['name']) for hit in res['hits']['hits']]
            return genres
        except NotFoundError:
            return []

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        cache_key = self._generate_cache_key('get_genre_by_id', genre_id=genre_id)
        genre = await self._get_genre_from_cache(cache_key)
        if not genre:
            genre = await self._get_genre_by_id_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(cache_key, genre)
        return genre

    async def _get_genre_by_id_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            res = await self.elastic.get(index="genres", id=genre_id)
            return Genre(uuid=res['_id'], name=res['_source']['name'])
        except NotFoundError:
            return None

    def _generate_cache_key(self, method: str, **kwargs) -> str:
        query_str = json.dumps(kwargs, sort_keys=True)
        key = f'{method}:{query_str}'
        return hashlib.sha256(key.encode()).hexdigest()

    async def _get_genres_from_cache(self, cache_key: str) -> Optional[List[Genre]]:
        genres = await self.redis.get(cache_key)
        if not genres:
            return None
        return [Genre.parse_raw(genre) for genre in json.loads(genres)]

    async def _put_genres_to_cache(self, cache_key: str, genres: List[Genre]):
        await self.redis.set(cache_key, json.dumps([genre.json() for genre in genres]), GENRES_CACHE_EXPIRE_IN_SECONDS)

    async def _get_genre_from_cache(self, cache_key: str) -> Optional[Genre]:
        genre = await self.redis.get(cache_key)
        if not genre:
            return None
        return Genre.parse_raw(genre)

    async def _put_genre_to_cache(self, cache_key: str, genre: Genre):
        await self.redis.set(cache_key, genre.json(), GENRES_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(redis, elastic)
