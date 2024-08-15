from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis


class RedisInter:
    def __init__(self):
        self.redis: Optional[Redis] = None

    async def _put_to_cache(self, key: str, value: str, time: int):
        await self.redis.set(key, value, time)

    async def _get_from_cache(self, key: str):
        value = await self.redis.get(key)
        return value or None
