from pathlib import Path
import redis.asyncio as redis

from gateway.core.config import settings


class RedisService:

    def __init__(self):
        if settings.REDIS_URL:
            self.pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=20
            )
        else:
            self.pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                max_connections=20
            )

        self.client = redis.Redis(connection_pool=self.pool)
        self._rate_limit_script = None

        script_path = (
            Path(__file__).parent.parent
            / "scripts"
            / "rate_limit.lua"
        )

        with open(script_path, "r") as f:
            self.lua_content = f.read()

        self.rate_limit_script = self.client.register_script(self.lua_content)

    def get_client(self) -> redis.Redis:
        return self.client

    async def close(self):
        await self.client.aclose()
        await self.pool.aclose()


redis_service = RedisService()