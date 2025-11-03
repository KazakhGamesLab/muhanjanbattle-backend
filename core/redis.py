from redis.asyncio import Redis
from config import settings

redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)