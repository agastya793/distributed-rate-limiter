from fastapi import APIRouter, Header, HTTPException, status, Depends

from gateway.core.config import settings
from gateway.models.admin import (
    RateLimitRequest,
    UserRoleRequest,
)

from gateway.services.user_limit_service import UserLimitService
from gateway.services.api_key_service import APIKeyService
from gateway.services.metrics_service import metrics_service


def verify_admin_key(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    if not x_admin_key or x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Admin-Key header"
        )
    return x_admin_key


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(verify_admin_key)]
)

user_limit_service = UserLimitService()
api_key_service = APIKeyService()


# -------------------------
# API Keys
# -------------------------

@router.post("/api-key/{client}")
async def generate_api_key(client: str):

    api_key = await api_key_service.generate_api_key(client)

    return {
        "client": client,
        "api_key": api_key
    }


# -------------------------
# Rate Limits
# -------------------------

@router.post("/rate-limit")
async def set_rate_limit(request: RateLimitRequest):

    await user_limit_service.set_limit(
        request.client,
        request.limit
    )

    return {
        "message": "Rate limit updated"
    }


@router.get("/rate-limits")
async def get_all_limits():

    return await user_limit_service.get_all_limits()


@router.get("/rate-limit/{client}")
async def get_limit(client: str):

    return {
        "client": client,
        "limit": await user_limit_service.get_limit(client)
    }


@router.delete("/rate-limit/{client}")
async def remove_limit(client: str):

    await user_limit_service.remove_limit(client)

    return {
        "message": "Custom rate limit removed"
    }


# -------------------------
# Roles
# -------------------------

@router.post("/role")
async def assign_role(request: UserRoleRequest):

    await user_limit_service.set_role(
        request.client,
        request.role
    )

    return {
        "message": f"{request.client} assigned role '{request.role}'"
    }


# -------------------------
# Whitelist
# -------------------------

@router.post("/whitelist/{client}")
async def whitelist(client: str):

    await user_limit_service.whitelist_client(client)

    return {
        "message": f"{client} added to whitelist"
    }


# -------------------------
# Blacklist
# -------------------------

@router.post("/blacklist/{client}")
async def blacklist(client: str):

    await user_limit_service.blacklist_client(client)

    return {
        "message": f"{client} added to blacklist"
    }


@router.delete("/blacklist/{client}")
async def remove_blacklist(client: str):

    await user_limit_service.remove_blacklist(client)

    return {
        "message": f"{client} removed from blacklist"
    }


@router.delete("/api-key/{api_key}")
async def revoke_api_key(api_key: str):

    await api_key_service.revoke_api_key(api_key)

    return {
        "message": "API Key revoked successfully"
    }


@router.get("/metrics")
async def metrics():

    return await metrics_service.get_metrics()


@router.delete("/metrics")
async def reset_metrics():

    await metrics_service.reset()

    return {
        "message": "Metrics reset successfully"
    }