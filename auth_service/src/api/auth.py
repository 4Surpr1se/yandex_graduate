from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import UserAuth
from src.services.auth import authenticate_user, create_tokens
from src.db.postgres import get_session
from src.core.config import settings

router = APIRouter()

@router.post('/login', status_code=status.HTTP_200_OK)
async def login(user_auth: UserAuth, response: Response, db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(user_auth.login, user_auth.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = await create_tokens(user)
    
    response.set_cookie(key="access_token", value=tokens.access_token, httponly=True, max_age=60*settings.access_token_expire_minutes)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, max_age=60*60*24*settings.refresh_token_expire_days)
    
    response.status_code = status.HTTP_200_OK
    return response
