import pytest
from gateway.auth.jwt_handler import create_access_token


@pytest.mark.asyncio
async def test_users_without_auth_fails(async_client):
    response = await async_client.get("/users")
    assert response.status_code == 401
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_users_with_jwt_auth(async_client):
    token = create_access_token({"sub": "testuser", "username": "testuser", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/users", headers=headers)
    # If downstream microservice is reachable, returns 200 or 502/504 depending on network
    assert response.status_code in (200, 502, 504)


@pytest.mark.asyncio
async def test_products_without_auth_fails(async_client):
    response = await async_client.get("/products")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_api_key_lifecycle(async_client):
    admin_headers = {"X-Admin-Key": "admin-secret-key-12345"}
    
    # 1. Generate API key for client "integration_test_client"
    gen_res = await async_client.post("/admin/api-key/integration_test_client", headers=admin_headers)
    assert gen_res.status_code == 200
    api_key = gen_res.json()["api_key"]

    # 2. Use API key to query /users/limit
    client_headers = {"X-API-Key": api_key}
    limit_res = await async_client.get("/users/limit", headers=client_headers)
    assert limit_res.status_code == 200
    assert limit_res.json()["client"] == "integration_test_client"

    # 3. Revoke API key
    revoke_res = await async_client.delete(f"/admin/api-key/{api_key}", headers=admin_headers)
    assert revoke_res.status_code == 200
