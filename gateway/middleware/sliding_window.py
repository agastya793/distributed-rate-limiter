import time

from fastapi import Request
from fastapi.responses import JSONResponse

from gateway.services.redis_service import redis_service


class SlidingWindowRateLimiter:

    LIMIT = 5
    WINDOW = 60

    def __init__(self):
        self.redis = redis_service.get_client()

    async def __call__(self, request: Request, call_next):

        client_ip = request.client.host

        key = f"sliding:{client_ip}"

        now = time.time()

        window_start = now - self.WINDOW

        # Remove timestamps outside the window
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests still inside the window
        current_requests = self.redis.zcard(key)

        if current_requests >= self.LIMIT:

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded"
                }
            )

        # Add current request
        self.redis.zadd(
            key,
            {
                str(now): now
            }
        )

        self.redis.expire(
            key,
            self.WINDOW
        )

        response = await call_next(request)

        return response