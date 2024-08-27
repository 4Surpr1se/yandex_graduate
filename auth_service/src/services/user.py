from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from auth_service.src.schemas.user import UserCreate, UserInDB

async def create_user_service(user_create: UserCreate, db: AsyncSession) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
