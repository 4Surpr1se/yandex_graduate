from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.schemas.user_activity import LikeRequest
from src.services.like_service import LikeService
from src.services.auth import verify_jwt

router = APIRouter()


@router.post("/")
async def add_like(request: LikeRequest, auth=Depends(verify_jwt)):
    res = await LikeService.add_like(user_id=request.user_id, item_id=request.item_id, score=request.score)
    if res:
        return {"status": "success"}
    else:
        return {"status": "fail"}


@router.delete("/{like_id}")
async def remove_like(user_id: UUID, item_id: UUID, auth=Depends(verify_jwt)):
    try:
        await LikeService.remove_like(user_id=user_id, item_id=item_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
