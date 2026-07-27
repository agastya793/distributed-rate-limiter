import pytest
from gateway.auth.jwt_handler import create_access_token, verify_token


@pytest.mark.asyncio
async def test_login_success(async_client):
    response = await async_client.post(
        "/auth/login",
        json={"username": "shubham", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_jwt_token_encode_decode():
    payload_data = {"sub": "test_user", "role": "admin"}
    token = create_access_token(payload_data)
    decoded = verify_token(token)

    assert decoded is not None
    assert decoded["sub"] == "test_user"
    assert decoded["role"] == "admin"


def test_jwt_invalid_token():
    decoded = verify_token("invalid_token_string")
    assert decoded is None
