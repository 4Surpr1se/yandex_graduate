from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

Base = declarative_base()
engine = create_async_engine(f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}'
                             f'@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}',
                             echo=True, future=True
                             )
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with Session() as session:
        yield session

