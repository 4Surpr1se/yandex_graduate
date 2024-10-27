from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint
from beanie import PydanticObjectId

from src.models.UGC import Review
from src.schemas.user_activity import ReviewRequest
from src.services.review_service import ReviewService
from src.services.auth import verify_jwt

router = APIRouter()


@router.post("/")
async def add_review(request: ReviewRequest, auth=Depends(verify_jwt)):
    res = await ReviewService.add_review(user_id=request.user_id, item_id=request.item_id,
                                         rating=request.rating, comment=request.comment)
    if res:
        return {"status": "review added"}
    return {"status": "review already exists"}



@router.put("/{review_id}")
async def update_review(request: ReviewRequest, auth=Depends(verify_jwt)):
    try:
        await ReviewService.update_review(user_id=request.user_id, item_id=request.item_id,
                                          rating=request.rating, comment=request.comment)
        return {"status": "review updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{review_id}")
async def remove_review(user_id: UUID, item_id: UUID, auth=Depends(verify_jwt)):
    try:
        await ReviewService.remove_review(user_id=user_id, item_id=item_id,)
        return {"status": "review removed"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/item/{item_id}")
async def get_item_reviews(item_id: UUID, auth=Depends(verify_jwt)):
    reviews = await ReviewService.get_item_reviews(item_id=item_id)
    return {"reviews": reviews}
