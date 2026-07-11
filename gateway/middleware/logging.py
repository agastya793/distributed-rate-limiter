import time

from fastapi import Request


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000

        print(
            f"{request.method} "
            f"{request.url.path} "
            f"{response.status_code} "
            f"{process_time:.2f} ms"
        )

        return response