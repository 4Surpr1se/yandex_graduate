from functools import lru_cache
from typing import List, Optional

from fastapi import Depends, Request
from fastapi.datastructures import QueryParams
from pydantic import BaseModel

from db.abstract_storage import AbstractCache, AbstractDataStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.films import Film
from services.base_service import BasePluralItemsService, ItemsModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FilmsService(BasePluralItemsService):
  
    def __init__(self, cache: AbstractCache, storage: AbstractDataStorage):
        super().__init__(cache, storage)
        self.index = 'movies'
        self.model: BaseModel = Film
        self.service_name = 'films'

    def _generate_body(self, query_params: QueryParams) -> dict:
        logging.info(f"Generating body for query params: {query_params}")

        page_size = int(query_params.get('page_size', 50))
        page_number = int(query_params.get('page', 1))
        genre_id = query_params.get('genre')

        filters = []
        if 'rating' in query_params:
            filters.append({
                "range": {
                    "imdb_rating": {
                        "gte": float(query_params.get('rating'))
                    }
                }
            })

        genre_filter = {
            'nested': {
                'path': 'genres',
                'query': {
                    'bool': {
                        'must': [{'match': {'genres.id': genre_id}}]
                    }
                }
            }
        } if genre_id else {'match_all': {}}

        body = {
            'sort': [
                {
                    'imdb_rating': {
                        'order': 'desc' if query_params.get('sort', '-imdb_rating') == '-imdb_rating' else 'asc'},
                }
            ],
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'bool': {
                    'must': filters + [genre_filter]
                }
            }
        }

        logging.info(f"Generated Elasticsearch query body: {body}")

        return body

    async def get_items(self, request: Request, query_params: QueryParams = None) -> Optional[ItemsModel]:
        roles = await self.get_roles(request)
        query_params = dict(query_params)
        query_params['roles'] = roles
        if 'premium' not in roles and 'admin' not in roles:
            query_params = query_params or QueryParams()
            query_params = dict(query_params)
            query_params['roles'] = roles
            query_params['rating'] = '8.0'

            if 'subscriber' not in roles:
                query_params['page'] = '1'
        logging.info(f"!!!!!!!!Текущие роли {query_params}")
        return await super().get_items(query_params=query_params)


@lru_cache()
def get_films_service(
        cache: AbstractCache = Depends(get_redis),
        storage: AbstractDataStorage = Depends(get_elastic),
) -> FilmsService:
    return FilmsService(cache, storage)
