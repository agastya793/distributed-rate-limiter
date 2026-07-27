import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from gateway.core.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        correlation_id = getattr(request.state, "correlation_id", "N/A")

        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Process-Time"] = f"{process_time}ms"

        client_host = request.client.host if request.client else "unknown"

        log_data = {
            "extra_data": {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": process_time,
                "client_ip": client_host,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        }

        logger.info(
            f"HTTP {request.method} {request.url.path} {response.status_code} ({process_time}ms)",
            extra=log_data
        )

        return response