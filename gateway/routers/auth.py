from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from gateway.auth.jwt_handler import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    # In production, validate user against DB/Auth service
    if not credentials.username or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )

    token = create_access_token(
        data={
            "sub": credentials.username,
            "username": credentials.username,
            "role": "user"
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }