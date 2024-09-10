from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

Base = declarative_base()

db_engine = create_async_engine(
    f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}'
    f'@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}',
    echo=True, future=True
)

async_session = sessionmaker(
    db_engine, class_=AsyncSession, expire_on_commit=False
)


# Подключение к целевой базе данных для выполнения операций с таблицами
async def create_tables() -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")


async def purge_tables() -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Tables dropped successfully!")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
