from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.core.config import settings
from src.models.UGC import Favorite, Like, Review


async def init_db():
    client = AsyncIOMotorClient(f"mongodb://{settings.mongo_user}@{settings.mongo_password}"
                                f"{settings.mongo_host}:{settings.mongo_port}/{settings.mongo_db}")
    await init_beanie(database=client.get_default_database(), document_models=[Favorite, Like, Review])
