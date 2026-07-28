from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from gateway.core.config import settings
from gateway.exceptions.handlers import global_exception_handler
from gateway.middleware.correlation import CorrelationIdMiddleware
from gateway.middleware.logging import LoggingMiddleware
from gateway.middleware.metrics_middleware import MetricsMiddleware
from gateway.middleware.security_headers import SecurityHeadersMiddleware
from gateway.middleware.sliding_window import SlidingWindowRateLimiter
from gateway.routers import admin, auth, product, user
from gateway.services.proxy_service import proxy_service
from gateway.services.redis_service import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_service.close()
    await proxy_service.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production API Gateway featuring Distributed Sliding Window Rate Limiting, JWT Auth, API Keys, Reverse Proxying, and Observability.",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT Bearer Token"
        },
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter Client X-API-Key Header"
        },
        "AdminKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Admin-Key",
            "description": "Enter X-Admin-Key for Admin Endpoints"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_exception_handler(
    Exception,
    global_exception_handler
)

# Register Middlewares in Execution Order
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SlidingWindowRateLimiter)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    user.router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    product.router,
    prefix="/products",
    tags=["Products"]
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

from fastapi.staticfiles import StaticFiles

app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="dashboard")


@app.get("/")
def root():
    return {
        "success": True,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Distributed Rate Limiter Gateway is running"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "service": settings.APP_NAME,
        "status": "healthy",
        "version": settings.APP_VERSION
    }
