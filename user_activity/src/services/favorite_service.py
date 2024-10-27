from typing import List
from uuid import UUID
from src.models.UGC import Favorite


class FavoriteService:
    @staticmethod
    async def add_favorite(user_id: UUID, item_id: UUID) -> bool:
        existing_favorite = await Favorite.find_one({"user_id": user_id, "item_id": item_id})

        if not existing_favorite:
            favorite = Favorite(user_id=user_id, item_id=item_id)
            await favorite.insert()
            return True
        return False

    @staticmethod
    async def remove_favorite(user_id: UUID, item_id: UUID):
        favorite = await Favorite.find_one({"user_id": user_id, "item_id": item_id})
        if favorite:
            await favorite.delete()
        else:
            raise ValueError("Favorite not found")

    @staticmethod
    async def get_user_favorites(user_id: UUID) -> List[Favorite]:
        return await Favorite.find(Favorite.user_id == user_id).to_list()
