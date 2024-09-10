from datetime import datetime, timedelta
from jose import JWTError, jwt

from werkzeug.security import check_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from src.models.user import User
from src.schemas.auth import Token
from src.db.redis import redis_client
from src.models.login_history import UserLogin


def create_access_token(data: dict, roles: list[str], expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode["roles"] = roles
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: dict, roles: list[str], expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode["roles"] = roles
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def authenticate_user(login: str, password: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.login == login))
    user = result.scalars().first()

    if user and check_password_hash(user.password, password):

        user_login = UserLogin(user_id = user.id)
        db.add(user_login)
        await db.commit()
        await db.refresh(user_login)

        return user
    return None

async def create_tokens(user: User, db: AsyncSession) -> Token:
    roles = [role.name for role in user.roles]

    access_token = create_access_token(data={"sub": user.login}, roles=roles)
    refresh_token = create_refresh_token(data={"sub": user.login}, roles=roles)

    user.refresh_token = refresh_token
    db.add(user)
    await db.commit() 
    await db.refresh(user)

    return Token(access_token=access_token, refresh_token=refresh_token)


async def decode_token(token: str) -> dict | None:
    is_invalid = await redis_client.get(token)
    if is_invalid:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None
