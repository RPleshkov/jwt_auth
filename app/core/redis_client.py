from typing import Self

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import settings


class RedisHelper:
    def __init__(
        self,
        host: str = settings.redis.host,
        port: int = settings.redis.port,
        db: int = settings.redis.db,
        max_connections: int = settings.redis.max_connections,
    ):
        self.client: Redis | None = None
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=max_connections,
        )

    async def __aenter__(self) -> Self:
        if not self.client:
            self.client = redis.Redis.from_pool(self.pool)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.close()
            self.client = None

    async def add_token_to_blacklist(
        self,
        token_id: str,
        ex: int = settings.security.jwt.access_token_expire_minutes,
    ):
        await self.client.set(token_id, "blacklisted", ex=ex * 60)  # type: ignore

    async def is_blacklisted_token(self, token_id: str) -> bool:
        result = await self.client.get(token_id)  # type: ignore
        return bool(result)
