#from redis import asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB


# redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
#
# async def get_redis():
#     return redis

import redis.asyncio as aioredis

def get_redis():
    return aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB
    )