from fastapi import Depends
from core.redis import redis_client
from core.database import get_db
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

async def get_redis() -> Redis:
    return redis_client