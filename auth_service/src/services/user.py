from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from werkzeug.security import generate_password_hash

from src.core.config import settings
from src.db.redis import redis_client
from src.services.auth import decode_token, create_tokens
from src.models.user import User
from src.models.role import Role
from src.schemas.user import UserCreate, UserInDB, UpdateResponse


async def create_user_service(user_create: UserCreate, db: AsyncSession, role: str = 'subscriber') -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    db_role = await get_or_create_role(db, role=role)

    if db_role not in user.roles:
        user.roles.append(db_role)
        await db.commit()
        await db.refresh(user)

    return user


async def get_or_create_role(db: AsyncSession, role: str) -> Role:
    result = await db.execute(select(Role).filter_by(name=role))
    db_role = result.scalars().first()

    if not db_role:
        await seed_roles(db)
        result = await db.execute(select(Role).filter_by(name=role))
        db_role = result.scalars().first()

    return db_role


async def seed_roles(db: AsyncSession):
    roles = ['subscriber', 'premium', 'admin']
    existing_roles = await db.execute(select(Role.name))
    existing_role_names = {row[0] for row in existing_roles}

    for role_name in roles:
        if role_name not in existing_role_names:
            db.add(Role(name=role_name))
    await db.commit()


async def update_login_service(db: AsyncSession, new_login: str,
                               access_token: str
                               ) -> Response | None:

    user = await get_user_by_token(db, access_token)
    if not user:
        return

    existing_user = await db.execute(select(User).where(User.login == new_login))
    existing_user = existing_user.unique().scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already in use. Please choose another login."
        )
    user.login = new_login
    await db.commit()

    await redis_client.setex(access_token, settings.access_token_expire_minutes * 60, "invalid")
    tokens = await create_tokens(user, db)

    response = Response()
    response.status_code = status.HTTP_200_OK
    response.set_cookie(key="access_token", value=tokens.access_token, httponly=True,
                        max_age=60 * settings.access_token_expire_minutes)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True,
                        max_age=60 * 60 * 24 * settings.refresh_token_expire_days)
    return response


async def update_password_service(db: AsyncSession, new_password: str, access_token: str) -> UpdateResponse | None:
    user = await get_user_by_token(db, access_token)
    if not user:
        return
    user.password = generate_password_hash(new_password)
    await db.commit()
    return UpdateResponse(success=True,
                          message=f"User password changed successfully.")


async def get_user_by_token(db: AsyncSession, access_token: str) -> User | None:
    access_token = await decode_token(access_token)

    if access_token is None or not (login := access_token.get('sub')):
        return

    user = await db.execute(select(User).where(User.login == login))
    user = user.unique().scalar_one_or_none()
    return user


async def get_user_by_login(login: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.login == login))
    user = result.scalars().first()
    return user


async def update_user_refresh_token(user: User, refresh_token: str, db: AsyncSession):
    user.refresh_token = refresh_token
    db.add(user)
    await db.commit()
    await db.refresh(user)
