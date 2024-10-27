from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from beanie import PydanticObjectId

from src.schemas.user_activity import FavoriteRequest
from src.services.favorite_service import FavoriteService
from src.services.auth import verify_jwt

router = APIRouter()


@router.post("/")
async def add_favorite(request: FavoriteRequest, auth=Depends(verify_jwt)):
    res = await FavoriteService.add_favorite(user_id=request.user_id, item_id=request.item_id)
    if res:
        return {"status": "favorite added"}
    return {"status": "favorite already added"}


@router.delete("/{favorite_id}")
async def remove_favorite(request: FavoriteRequest, auth=Depends(verify_jwt)):
    try:
        await FavoriteService.remove_favorite(user_id=request.user_id, item_id=request.item_id)
        return {"status": "favorite removed"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_favorites(user_id: UUID, auth=Depends(verify_jwt)):
    favorites = await FavoriteService.get_user_favorites(user_id=user_id)
    return {"favorites": favorites}
