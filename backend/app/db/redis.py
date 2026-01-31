import redis.asyncio as aredis
import redis
import json
from typing import Any, Optional
from app.core.config import settings

redis_pool = None
sync_redis_pool = None

# Async Redis
async def init_redis_pool():
    global redis_pool
    redis_pool = aredis.ConnectionPool.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True,
        encoding="utf-8",
    )

async def get_redis():
    if redis_pool is None:
        await init_redis_pool()
    return aredis.Redis(connection_pool=redis_pool)

async def close_redis_pool():
    if redis_pool:
        await redis_pool.disconnect()

# Sync Redis
def init_sync_redis_pool():
    global sync_redis_pool
    sync_redis_pool = redis.ConnectionPool.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True,
        encoding="utf-8",
    )

def get_sync_redis():
    if sync_redis_pool is None:
        init_sync_redis_pool()
    return redis.Redis(connection_pool=sync_redis_pool)


# Cache helpers
async def get_cached_json(key: str) -> Optional[Any]:
    redis_client = await get_redis()
    cached_data = await redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

async def set_cached_json(key: str, data: Any, ex: int):
    redis_client = await get_redis()
    await redis_client.set(key, json.dumps(data), ex=ex)

