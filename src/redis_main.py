import aioredis as redis
from aioredis.client import Pipeline

from src.config import REDIS_HOST, REDIS_PORT

connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


async def get_async_redis_session() -> Pipeline:
    async with connection.pipeline(transaction=True) as session:
        yield session
