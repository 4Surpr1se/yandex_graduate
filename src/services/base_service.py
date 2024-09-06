from http import HTTPStatus
from typing import Optional, List, TypeVar, Any
import json
import hashlib

from fastapi import Request, HTTPException
from fastapi.datastructures import QueryParams
from pydantic import BaseModel, RootModel

from services.auth import verify_jwt
from core.cache_config import cache_config
from db.abstract_storage import AbstractCache, AbstractDataStorage


T = TypeVar('T', bound=BaseModel)


class ItemsModel(RootModel[List[T]]):
    pass


class BaseSingleItemService:

    def __init__(self, cache: AbstractCache, storage: AbstractDataStorage):
        self.cache = cache
        self.storage = storage
        self.index: Optional[str] = None
        self.model: Optional[BaseModel] = None
        self.service_name: Optional[str] = None

    async def get_by_id(self, item_id: str, request: Request) -> Optional[BaseModel]:
        roles = await self.get_roles(request=request)
        if not roles:
            raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                                detail='Not allowed for unauthorized users')
        item = await self._get_item_from_cache(item_id)
        if not item:
            item = await self._get_item_by_id_from_storage(item_id)
            if not item:
                return None
            await self._put_item_to_cache(item)
        return item

    async def _put_item_to_cache(self, item: BaseModel):
        item_id_str = f'{self.model}:{str(item.uuid)}'
        await self.cache.set(item_id_str,
                                 item.json(),
                                 cache_config.get_expiration_time(self.service_name))

    async def _get_item_by_id_from_storage(self, item_id: str) -> Optional[BaseModel]:
        item = await self.storage.get_by_id(self.index, item_id)
        return self.model(**item) if item else None

    async def _get_item_from_cache(self, item_id: str) -> Optional[BaseModel]:
        data = await self.cache.get(item_id)
        return self.model.model_validate_json(data) if data else None

    async def get_roles(self, request: Request) -> List[Any] | None:
        try:
            response = await verify_jwt(request)
            return response['roles']
        except HTTPException:
            return []


class BasePluralItemsService(BaseSingleItemService):

    async def get_items(self, query_params: QueryParams = None) -> Optional[ItemsModel]:
        if query_params is None:
            query_params = {}
        cache = self._generate_cache(query_params)
        items = await self._get_items_from_cache(cache)
        if not items:
            items = await self._get_items_from_storage(query_params)
            if not items:
                return None
            await self._put_items_to_cache(cache, items)
        return items

    async def _get_items_from_storage(self, query_params: QueryParams) -> Optional[ItemsModel]:
        body = self._generate_body(query_params)
        if not body:
            return None
        items = await self.storage.get_list(self.index, body)
        return ItemsModel[self.model](root=items) if items else None

    async def _get_items_from_cache(self, cache: str) -> Optional[ItemsModel]:
        items = await self.cache.get(cache)
        return ItemsModel[self.model].model_validate_json(items) if items else None

    async def _put_items_to_cache(self, cache: str, items: ItemsModel) -> None:
        await self.cache.set(cache, items.json(), cache_config.get_expiration_time(self.service_name))

    def _generate_cache(self, query_params: QueryParams) -> str:
        query_str = json.dumps(sorted(query_params.items())) if query_params else ''
        key = f'{self.service_name}:{query_str}'
        cache_key = hashlib.sha256(key.encode()).hexdigest()
        return cache_key

    def _generate_body(self, query_params: QueryParams) -> dict:
        pass
