import aioredis
import os
from dotenv import load_dotenv
import json

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_cache(key: str):
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value: dict, expire: int = 60):
    await redis.set(key, json.dumps(value), ex=expire)

async def delete_cache(key: str):
    await redis.delete(key)