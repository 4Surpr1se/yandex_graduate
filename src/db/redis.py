from typing import Optional

from redis.asyncio import Redis

from db.abstract_storage import AbstractCache

redis: Optional[Redis] = None

class RedisCache(AbstractCache):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expiration_time: int):
        await self.redis.set(key, value, expiration_time)

async def get_redis() -> RedisCache:
    return RedisCache(redis)
