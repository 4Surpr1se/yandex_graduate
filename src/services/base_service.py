from typing import Optional, List, TypeVar
import json
import hashlib


from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from fastapi.datastructures import QueryParams
from pydantic import BaseModel, RootModel

from core.cache_config import cache_config
from db.elastic import ElasticInter
from db.redis import RedisInter


T = TypeVar('T', bound=BaseModel)


class ItemsModel(RootModel[List[T]]):
    pass


class BaseSingleItemService(ElasticInter, RedisInter):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index: Optional[str] = None
        self.model: Optional[BaseModel] = None
        self.service_name: Optional[str] = None

    async def get_by_id(self, item_id: str) -> Optional[BaseModel]:
        item = await self._get_item_from_cache(item_id)
        if not item:
            item = await self._get_item_by_id_from_elastic(item_id)
            if not item:
                return None
            await self._put_item_to_cache(item)
        return item

    async def _put_item_to_cache(self, item: BaseModel):
        item_id_str = f'{self.model}:{str(item.uuid)}'
        await self._put_to_cache(item_id_str,
                                 item.json(),
                                 cache_config.get_expiration_time(self.service_name))

    async def _get_item_by_id_from_elastic(self, item_id: str) -> Optional[BaseModel]:
        item = await self._get_by_id_from_elastic(item_id)
        return self.model(**item) if item else None

    async def _get_item_from_cache(self, item_id: str) -> Optional[BaseModel]:
        data = await self._get_from_cache(item_id)
        return self.model.model_validate_json(data) if data else None


class BasePluralItemsService(BaseSingleItemService):

    async def get_items(self, query_params: QueryParams = None) -> Optional[ItemsModel]:
        if query_params is None:
            query_params = {}
        cache = self._generate_cache(query_params)
        items = await self._get_items_from_cache(cache)
        if not items:
            items = await self._get_items_from_elastic(query_params)
            if not items:
                return None
            await self._put_items_to_cache(cache, items)
        return items

    async def _get_items_from_elastic(self, query_params: QueryParams) -> Optional[ItemsModel]:
        body = self._generate_body(query_params)
        if not body:
            return None
        hits = await self._get_hits_from_elastic(body)
        items = [self.model(**hit['_source']) for hit in hits]
        return ItemsModel[self.model](root=items) if items else None

    async def _get_items_from_cache(self, cache: str) -> Optional[ItemsModel]:
        items = await self._get_from_cache(cache)
        return ItemsModel[self.model].model_validate_json(items) if items else None

    async def _put_items_to_cache(self, cache: str, items: ItemsModel) -> None:
        await self._put_to_cache(cache, items.json(), cache_config.get_expiration_time(self.service_name))

    def _generate_cache(self, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items())) if query_params else ''
        key = f'{self.service_name}:{query_str}'
        cache_key = hashlib.sha256(key.encode()).hexdigest()
        return cache_key

    def _generate_body(self, query_params: QueryParams) -> dict:
        pass
