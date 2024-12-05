from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends
from db.billing_postgres import get_session
from models.film_purchase import FilmPurchase


class AccessChecker:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def has_access(self, user_id: str, film_id: str) -> bool:
        query = (
            select(1)
            .where(
                (FilmPurchase.user_id == user_id)
                & (FilmPurchase.movie_id == film_id)
            )
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar() is not None


def get_access_checker(session: AsyncSession = Depends(get_session)) -> AccessChecker:
    return AccessChecker(session)
