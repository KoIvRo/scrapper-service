import redis.asyncio as redis
from redis.asyncio import RedisCluster


class CacheManager:
    """Управление кэшом."""

    def __init__(self, port: str, host: int, ttl: int) -> None:
        self._client = RedisCluster(host=host, port=port)
        self._ttl = ttl
