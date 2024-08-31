# src/db/redis.py
import redis.asyncio as redis
from src.core.config import settings

redis_client = redis.Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True
)