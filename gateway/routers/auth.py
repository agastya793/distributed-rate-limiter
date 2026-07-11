from fastapi import APIRouter
from gateway.auth.jwt_handler import create_access_token

router = APIRouter()

@router.post("/login")
def login():
    try:
        token = create_access_token(
            {
                "username": "shubham"
            }
        )

        return {
            "access_token": token
        }

    except Exception as e:
        return {
            "error": str(e)
        }