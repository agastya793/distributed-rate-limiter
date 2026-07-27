from fastapi import APIRouter, Depends, Request

from gateway.auth.dependencies import get_current_user
from gateway.core.config import settings
from gateway.services.proxy_service import proxy_service

router = APIRouter()


# -----------------------------
# Proxy: /products
# -----------------------------
@router.api_route(
    "",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_products(
    request: Request,
    user=Depends(get_current_user)
):
    target_url = f"{settings.PRODUCT_SERVICE_URL}/products"

    return await proxy_service.forward_request(
        request=request,
        target_url=target_url
    )


# -----------------------------
# Proxy: /products/{path}
# -----------------------------
@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_product_path(
    path: str,
    request: Request,
    user=Depends(get_current_user)
):
    target_url = f"{settings.PRODUCT_SERVICE_URL}/products/{path}"

    return await proxy_service.forward_request(
        request=request,
        target_url=target_url
    )