from functools import lru_cache

from pydantic import BaseModel
from http import HTTPStatus 
from fastapi import HTTPException, Request, Depends

from db.abstract_storage import AbstractCache, AbstractDataStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base_service import BaseSingleItemService
from services.access_checker import AccessChecker, get_access_checker


from services.access_checker import AccessChecker, get_access_checker


class FilmService(BaseSingleItemService):
    def __init__(self, cache: AbstractCache, storage: AbstractDataStorage, access_checker: AccessChecker):
        super().__init__(cache, storage)
        self.access_checker = access_checker
        self.index = 'movies'
        self.model: BaseModel = Film
        self.service_name = 'film'

    async def get_by_id(self, item_id: str, request: Request, response: Response) -> Optional[BaseModel]:
        roles = await self.get_roles(request=request, response=response)
        user_id = request.headers.get("X-User-Id")
        
        if not roles:
            raise HTTPException(
                status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                detail="Not allowed for unauthorized users"
            )

        if 'premium' not in roles:
            if not user_id:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="User ID is required for access"
                )
            has_access = await self.access_checker.has_access(user_id=user_id, film_id=item_id)
            if not has_access:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Access to this film is restricted"
                )

        item = await self._get_item_from_cache(item_id)
        if not item:
            item = await self._get_item_by_id_from_storage(item_id)
            if not item:
                return None
            await self._put_item_to_cache(item)
        return item


@lru_cache()
def get_film_service(
    cache: AbstractCache = Depends(get_redis),
    storage: AbstractDataStorage = Depends(get_elastic),
    access_checker: AccessChecker = Depends(get_access_checker),
) -> FilmService:
    return FilmService(cache, storage, access_checker)
