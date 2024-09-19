from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.postgres import get_session
from src.db.redis import redis_client
from src.schemas.auth import UserAuth
from src.services.auth import (authenticate_user, create_access_token,
                               create_refresh_token, create_tokens,
                               decode_token)
from src.services.user import get_user_by_login, update_user_refresh_token

router = APIRouter()

@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: Request, user_auth: UserAuth, response: Response, db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(request, user_auth.login, user_auth.password, db)
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

    return {"login": payload.get("sub", "Unknown"),
            "roles": payload.get("roles", []),
            'user_id': payload.get('user_id')}


@router.post('/refresh', status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_session)):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    payload = await decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await get_user_by_login(payload.get("sub"), db)

    if not user or user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Генерация новых токенов
    new_access_token = create_access_token(data={"sub": user.login},
                                           roles=[role.name for role in user.roles], user_id=user.id)
    new_refresh_token = create_refresh_token(data={"sub": user.login},
                                             roles=[role.name for role in user.roles], user_id=user.id)

    await update_user_refresh_token(user, new_refresh_token, db)

    access_token_expires_in = settings.access_token_expire_minutes * 60
    refresh_token_expires_in = settings.refresh_token_expire_days * 24 * 60 * 60

    response.set_cookie(key="access_token", value=new_access_token,
                        httponly=True, max_age=access_token_expires_in)
    response.set_cookie(key="refresh_token", value=new_refresh_token,
                        httponly=True, max_age=refresh_token_expires_in)

    response.status_code = status.HTTP_200_OK

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "access_token_expires_in": access_token_expires_in,  # Время жизни access_token
        "refresh_token_expires_in": refresh_token_expires_in  # Время жизни refresh_token
    }
