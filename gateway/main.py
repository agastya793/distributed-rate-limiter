from fastapi import FastAPI, Request

from gateway.routers import product, user
from gateway.middleware.logging import LoggingMiddleware

from gateway.core.config import settings

from gateway.exceptions.handlers import global_exception_handler

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_exception_handler(
    Exception,
    global_exception_handler
)

from gateway.routers import auth
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)


logger = LoggingMiddleware()



from gateway.middleware.sliding_window import SlidingWindowRateLimiter
sliding = SlidingWindowRateLimiter()

@app.middleware("http")
async def logging(request: Request, call_next):
    return await logger(request, call_next)

@app.middleware("http")
async def sliding_window(request: Request, call_next):
    return await sliding(request, call_next)



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



