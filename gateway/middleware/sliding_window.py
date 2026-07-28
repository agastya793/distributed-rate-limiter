import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from gateway.services.redis_service import redis_service
from gateway.services.user_limit_service import UserLimitService
from gateway.services.api_key_service import APIKeyService
from gateway.auth.jwt_handler import verify_token


class SlidingWindowRateLimiter(BaseHTTPMiddleware):

    WINDOW = 60

    def __init__(self, app):
        super().__init__(app)
        self.user_limit_service = UserLimitService()
        self.api_key_service = APIKeyService()

    async def dispatch(self, request: Request, call_next):

        # ----------------------------
        # Public Endpoints
        # ----------------------------
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/docs/oauth2-redirect",
            "/auth/login",
        ]

        if (
            request.url.path in public_paths
            or request.url.path.startswith("/admin")
            or request.url.path.startswith("/dashboard")
        ):
            return await call_next(request)

        # ----------------------------
        # Dual Authentication (X-API-Key or Bearer JWT)
        # ----------------------------
        client = None
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")

        if api_key:
            try:
                client = await self.api_key_service.validate_api_key(api_key)
            except Exception:
                client = None
        elif auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = verify_token(token)
            if payload:
                client = payload.get("username") or payload.get("sub")

        if not client:
            return JSONResponse(
                status_code=401,
                content={"error": "Valid JWT Bearer token or X-API-Key is required"}
            )

        if isinstance(client, bytes):
            client = client.decode()

        # ----------------------------
        # Blacklist & Whitelist Checks
        # ----------------------------
        try:
            if await self.user_limit_service.is_blacklisted(client):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Client is blacklisted"}
                )

            if await self.user_limit_service.is_whitelisted(client):
                return await call_next(request)
        except Exception:
            pass

        # ----------------------------
        # Dynamic Rate Limit via Atomic Lua Script
        # ----------------------------
        try:
            limit = await self.user_limit_service.get_limit(client)
            key = f"sliding:{client}"
            now = time.time()

            allowed = await redis_service.rate_limit_script(
                keys=[key],
                args=[now, self.WINDOW, limit]
            )

            if allowed == 0:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "client": client,
                        "limit": limit,
                        "window": self.WINDOW
                    },
                    headers={
                        "Retry-After": str(self.WINDOW),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0"
                    }
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            return response
        except Exception:
            # Fallback if Redis is unavailable
            return await call_next(request)