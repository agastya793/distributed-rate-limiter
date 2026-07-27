import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from gateway.services.metrics_service import metrics_service


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        api_key = request.headers.get("X-API-Key", "anonymous")

        await metrics_service.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_id=api_key
        )

        return response
