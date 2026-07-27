from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from gateway.services.api_key_service import APIKeyService

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Client API Key for rate limiting and authentication"
)

api_key_service = APIKeyService()


async def verify_api_key(
    api_key: str = Security(api_key_header)
):

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key is required"
        )

    client = await api_key_service.validate_api_key(api_key)

    if client is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return client