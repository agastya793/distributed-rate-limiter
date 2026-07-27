from fastapi import APIRouter, Depends, Request

from gateway.auth.dependencies import get_current_user
from gateway.core.config import settings
from gateway.services.proxy_service import proxy_service
from gateway.services.user_limit_service import UserLimitService
from gateway.services.api_key_service import APIKeyService

router = APIRouter()

user_limit_service = UserLimitService()
api_service = APIKeyService()


# -----------------------------
# Local Endpoint
# -----------------------------
@router.get("/limit")
async def get_limit(request: Request):

    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return {
            "error": "API Key required"
        }

    client = await api_service.validate_api_key(api_key)

    if client is None:
        return {
            "error": "Invalid API Key"
        }

    return {
        "client": client,
        "limit": await user_limit_service.get_limit(client)
    }


# -----------------------------
# Proxy: /users
# -----------------------------
@router.api_route(
    "",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_users(
    request: Request,
    user=Depends(get_current_user)
):

    target_url = f"{settings.USER_SERVICE_URL}/users"

    return await proxy_service.forward_request(
        request=request,
        target_url=target_url
    )


# -----------------------------
# Proxy: /users/{path}
# -----------------------------
@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_user_path(
    path: str,
    request: Request,
    user=Depends(get_current_user)
):

    target_url = f"{settings.USER_SERVICE_URL}/users/{path}"

    return await proxy_service.forward_request(
        request=request,
        target_url=target_url
    )