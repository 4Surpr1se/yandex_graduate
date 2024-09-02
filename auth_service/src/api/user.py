from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.user import create_user_service, update_login_service, update_password_service
from src.schemas.user import UserCreate, UserInDB, UpdateResponse
from src.db.postgres import get_session

router = APIRouter()


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_session)) -> UserInDB:
    return await create_user_service(user_create, db)


@router.post('/update-login', response_model=UpdateResponse, status_code=status.HTTP_200_OK)
async def update_login(new_user_login: str,
                       request: Request,
                       db: AsyncSession = Depends(get_session)
                       ):
    access_token = request.cookies.get("access_token")
    response = await update_login_service(db, new_user_login, access_token)
    if not response:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return response


@router.post('/update-password', response_model=UpdateResponse, status_code=status.HTTP_200_OK)
async def update_password(new_user_password: str,
                          request: Request,
                          db: AsyncSession = Depends(get_session)
                          ):
    access_token = request.cookies.get('access_token')
    res = await update_password_service(db, new_user_password, access_token)
    if not res:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return res
