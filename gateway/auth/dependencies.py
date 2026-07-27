from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from gateway.auth.jwt_handler import verify_token
from gateway.auth.api_key import api_key_header, api_key_service

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    payload = verify_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


async def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    api_key: str = Security(api_key_header)
):
    # Option 1: JWT Authentication
    if credentials:
        payload = verify_token(credentials.credentials)
        if payload and "username" in payload:
            return payload["username"]

    # Option 2: API Key Authentication
    if api_key:
        client = await api_key_service.validate_api_key(api_key)
        if client:
            return client

    raise HTTPException(
        status_code=401,
        detail="Valid JWT Bearer token or X-API-Key is required"
    )