from aioredis.client import Pipeline
from fastapi import Depends

from src.redis_main import get_async_redis_session
from src.redis_manager.redis_manager import RedisManager


async def get_redis_manager(session: Pipeline = Depends(get_async_redis_session)) -> RedisManager:
    yield RedisManager(session)
