import redis.asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

def get_redis():
    return aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB
    )
