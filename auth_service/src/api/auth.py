from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import UserAuth
from src.services.auth import authenticate_user, create_tokens, decode_token
from src.db.postgres import get_session
from src.core.config import settings
from src.db.redis import redis_client

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
    
    tokens = await create_tokens(user, db)
    
    response.set_cookie(key="access_token", value=tokens.access_token, httponly=True, max_age=60*settings.access_token_expire_minutes)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, max_age=60*60*24*settings.refresh_token_expire_days)
    
    response.status_code = status.HTTP_200_OK
    return response


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
        )
        
    await redis_client.setex(
        access_token, 
        settings.access_token_expire_minutes * 60, 
        "invalid"
    )
    
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    response.status_code = status.HTTP_200_OK
    return {"msg": "Logged out successfully"}

@router.post('/verify_token', status_code=status.HTTP_200_OK)
async def verify_token(request: Request, db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
        )

    is_revoked = await redis_client.get(access_token)
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    try:
        payload = await decode_token(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    return {"login": payload.get("sub", "Unknown"), "roles": payload.get("roles", [])}
