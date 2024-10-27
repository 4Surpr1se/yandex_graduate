from uuid import UUID
from src.models.UGC import Like


class LikeService:
    @staticmethod
    async def add_like(user_id: UUID, item_id: UUID, score: int):
        if not await Like.find_one({"user_id": user_id, "item_id": item_id}):
            like = Like(user_id=user_id, item_id=item_id, score=score)
            await like.insert()
            return True
        return False

    @staticmethod
    async def remove_like(user_id: UUID, item_id: UUID):
        like = await Like.find_one({"user_id": user_id, "item_id": item_id})
        if like:
            await like.delete()
        else:
            raise ValueError("Like not found")
