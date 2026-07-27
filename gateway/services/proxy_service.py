import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse


class ProxyService:

    def __init__(self):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=50,
                max_connections=200
            ),
            timeout=httpx.Timeout(30.0, connect=5.0)
        )

    async def close(self):
        await self.client.aclose()

    async def forward_request(
        self,
        request: Request,
        target_url: str
    ) -> Response:
        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        if hasattr(request.state, "correlation_id"):
            headers["X-Request-ID"] = request.state.correlation_id

        # Forward body
        body = await request.body()

        try:
            target_response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body if body else None
            )

            # Filter headers to pass back
            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            response_headers = {
                k: v for k, v in target_response.headers.items()
                if k.lower() not in excluded_headers
            }

            return Response(
                content=target_response.content,
                status_code=target_response.status_code,
                headers=response_headers,
                media_type=target_response.headers.get("content-type")
            )

        except httpx.TimeoutException:
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Gateway Timeout",
                    "message": f"Target service at {target_url} timed out."
                }
            )

        except httpx.RequestError as exc:
            return JSONResponse(
                status_code=502,
                content={
                    "error": "Bad Gateway",
                    "message": f"Unable to reach target service: {str(exc)}"
                }
            )


proxy_service = ProxyService()