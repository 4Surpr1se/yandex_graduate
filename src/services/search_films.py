from functools import lru_cache
import hashlib
import json

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from fastapi.datastructures import QueryParams
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from .films import FilmsService


class SearchFilmsService(FilmsService):

    def _generate_cache(self, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items())) if query_params else ''
        key = f'{self.service_name}/search:{query_str}'
        cache_key = hashlib.sha256(key.encode()).hexdigest()
        return cache_key


    def _generate_body(self, query_params: QueryParams) -> dict | None:
        page_size = int(query_params.get('page_size', 50))
        page_number = int(query_params.get('page_number', 1))
        genre_id = query_params.get('genre')
        search_query = query_params.get('query')
        if not search_query:
            return None
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'bool': {
                    'must': [
                        {
                            'multi_match': {
                                'query': search_query,
                                'fields': ['title', "description"],
                                "type": "phrase"
                            }
                        }
                    ] if search_query else [],
                    'filter': [
                        {
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
                        }
                    ] if genre_id else []
                }
            }
        }
        return body


@lru_cache()
def search_films_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SearchFilmsService:
    return SearchFilmsService(redis, elastic)
