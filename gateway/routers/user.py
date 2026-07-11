from fastapi import APIRouter, Depends

from gateway.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/")
def get_users(
    user=Depends(get_current_user)
):
    return {
        "success": True,
        "message": "Users fetched successfully",
        "data": {
            "logged_in_user": user,
            "users": [
                "Alice",
                "Bob",
                "Charlie"
            ]
        }
    }    