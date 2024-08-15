from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import ElasticInter, get_elastic
from db.redis import RedisInter, get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(ElasticInter, RedisInter):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = 'movies'

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        film = await self._get_by_id_from_elastic(film_id)
        return Film(**film) if film else None

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self._get_from_cache(film_id)
        return Film.parse_raw(data) if data else None

    async def _put_film_to_cache(self, film: Film):
        film_id_str = f'film:{str(film.uuid)}'
        await self._put_to_cache(film_id_str, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
