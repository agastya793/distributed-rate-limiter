from pathlib import Path
import redis

from gateway.core.config import settings


class RedisService:

    def __init__(self):

        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

        script_path = (
            Path(__file__).parent.parent
            / "scripts"
            / "rate_limit.lua"
        )

        with open(script_path, "r") as f:
            self.rate_limit_script = self.client.register_script(
                f.read()
            )

    def get_client(self):
        return self.client
    
redis_service = RedisService()