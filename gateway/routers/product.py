from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_products():
    return {
        "service": "Product Service",
        "products": [
            "Laptop",
            "Phone",
            "Keyboard"
        ]
    }