from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from pydantic import BaseModel
from redis.asyncio import Redis

from db.elastic import ElasticInter, get_elastic
from db.redis import RedisInter, get_redis
from models.films import Film
from services.base_service import BasePluralItemsService


class FilmsService(BasePluralItemsService):
  
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = 'movies'
        self.model: BaseModel = Film
        self.service_name = 'films'
        
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
