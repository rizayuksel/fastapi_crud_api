"""
Redis cache utilities.

Simple caching layer for expensive queries.
"""

import json
from typing import Optional

import redis.asyncio as redis

from app.config import settings

# Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    return _redis_client


async def get_cache(key: str) -> Optional[dict]:
    """Get value from cache"""
    client = await get_redis()

    try:
        value = await client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        # If Redis fails, just skip cache
        print(f"Cache get error: {e}")

    return None


async def set_cache(key: str, value: dict, expire: int = 300) -> bool:
    """Set value in cache with expiration (default 5 min)"""
    client = await get_redis()

    try:
        await client.setex(key, expire, json.dumps(value, default=str))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


async def delete_cache(pattern: str) -> int:
    """Delete cache keys matching pattern"""
    client = await get_redis()

    try:
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
    except Exception as e:
        print(f"Cache delete error: {e}")

    return 0
