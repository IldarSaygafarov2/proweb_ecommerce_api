import json

from redis.asyncio import Redis

from app.core.config import settings


redis_client: Redis | None = None


async def init_redis_pool() -> None:
    global redis_client

    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await redis_client.ping()
    except Exception:
        redis_client = None


async def shutdown_redis_pool() -> None:
    if redis_client is not None:
        await redis_client.close()



async def get_json(key: str):
    if redis_client is None:
        return None

    value = await redis_client.get(key)
    if not value:
        return None

    return json.loads(value)  # .dumps()


async def set_json(key: str, payload, ttl: int | None = None):
    if redis_client is None:
        return None
    await redis_client.set(
        key,
        json.dumps(payload, default=str),
        ex=ttl
    )


async def delete_by_prefix(prefix: str):
    if redis_client is None:
        return

    keys = await redis_client.keys(f'{prefix}*')
    if keys:
        await redis_client.delete(*keys)


