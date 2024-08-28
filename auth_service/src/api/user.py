from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.user import create_user_service  # импортируем сервис для создания пользователя
from src.schemas.user import UserCreate, UserInDB
from src.db.postgres import get_session  # Импортируем функцию получения сессии

router = APIRouter()


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_session)) -> UserInDB:
    return await create_user_service(user_create, db)
