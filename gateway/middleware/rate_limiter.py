from fastapi import Request
from fastapi.responses import JSONResponse

from gateway.services.redis_service import redis_service


class RateLimiter:

    LIMIT = 5
    WINDOW = 60

    def __init__(self):
        self.redis = redis_service.get_client()

    async def __call__(self, request: Request, call_next):

        client_ip = request.client.host

        key = f"rate_limit:{client_ip}"

        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, self.WINDOW)

        if current > self.LIMIT:

            ttl = self.redis.ttl(key)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": ttl
                }
            )

        response = await call_next(request)

        return response