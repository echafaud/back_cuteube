from datetime import timedelta

from aioredis.client import Pipeline


class RedisManager:
    def __init__(self, redis_session: Pipeline):
        self.redis_session = redis_session

    async def set(self,
                  key: str,
                  value: str,
                  time: timedelta = None,
                  execute: bool = False):
        await self.redis_session.set(key, value, time)
        if execute:
            return await self.execute()

    async def get(self,
                  key: str,
                  execute: bool = False):
        result = await self.redis_session.get(key)
        if execute:
            return await self.execute()
        return result

    async def check_existing(self,
                             key: str,
                             execute: bool = False
                             ):
        exists = await self.redis_session.exists(key)
        if execute:
            return await self.execute()
        return exists

    async def get_time_exp(self,
                           key: str,
                           execute: bool = False):
        ttl = await self.redis_session.ttl(key)
        if execute:
            return await self.execute()
        return ttl

    async def execute(self):
        return await self.redis_session.execute()
