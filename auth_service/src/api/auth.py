# src/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import UserAuth, Token
from src.services.auth import authenticate_user, create_tokens
from src.db.postgres import get_session

router = APIRouter()

@router.post('/login', response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_auth: UserAuth, db: AsyncSession = Depends(get_session)) -> Token:
    user = await authenticate_user(user_auth.login, user_auth.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await create_tokens(user)
