from typing import List
from uuid import UUID
from src.models.UGC import Review


class ReviewService:
    @staticmethod
    async def add_review(user_id: UUID, item_id: UUID, rating: int, comment: str) -> bool:
        existing_review = await Review.find_one({"user_id": user_id, "item_id": item_id})
        if not existing_review:
            review = Review(user_id=user_id, item_id=item_id, rating=rating, comment=comment)
            await review.insert()
            return True
        return False

    @staticmethod
    async def update_review(user_id: UUID, item_id: UUID, rating: int, comment: str):
        review = await Review.find_one({"user_id": user_id, "item_id": item_id})
        if review:
            review.rating = rating
            review.comment = comment
            await review.save()
        else:
            raise ValueError("Review not found")

    @staticmethod
    async def remove_review(user_id: UUID, item_id: UUID):
        review = await Review.find_one({"user_id": user_id, "item_id": item_id})
        if review:
            await review.delete()
        else:
            raise ValueError("Review not found")

    @staticmethod
    async def get_item_reviews(item_id: UUID) -> List[Review]:
        return await Review.find(Review.item_id == item_id).to_list()
